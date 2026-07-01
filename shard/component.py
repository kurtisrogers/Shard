from __future__ import annotations

from functools import wraps
from typing import Any, Callable, ClassVar
from uuid import uuid4

from django.template import Context, Template
from django.template.loader import render_to_string
from django.utils.safestring import SafeString, mark_safe

from shard.exceptions import ActionNotFoundError, PropValidationError
from shard.props import Prop
from shard.slots import DEFAULT_SLOT, SlotContent
from shard.state import StateStore
from shard.styles import component_scope, load_scoped_styles


ACTION_MARKER = "__shard_action__"
IGNORED_PAYLOAD_KEYS = frozenset({"csrfmiddlewaretoken", "shard"})


def action(method: Callable) -> Callable:
    """Mark a component method as an HTMX-callable server action."""

    @wraps(method)
    def wrapper(self, state: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
        return method(self, state, *args, **kwargs)

    setattr(wrapper, ACTION_MARKER, True)
    return wrapper


class ComponentMeta(type):
    def __new__(mcs, name: str, bases: tuple[type, ...], namespace: dict[str, Any]):
        prop_fields: dict[str, Prop] = {}
        for base in reversed(bases):
            prop_fields.update(getattr(base, "_prop_fields", {}))

        for key, value in list(namespace.items()):
            if isinstance(value, Prop):
                prop_fields[key] = value.bind(key)
                namespace[key] = prop_fields[key]

        cls = super().__new__(mcs, name, bases, namespace)
        cls._prop_fields = prop_fields
        cls.component_name = namespace.get("component_name", name)
        return cls


class Component(metaclass=ComponentMeta):
    """Base class for Shard components.

    Declare props on the class, optional ``get_initial_state`` for server state,
    ``@action`` methods for HTMX, templates with ``{{ slots.default }}`` for
    wrapped content, and a co-located ``.css`` file for scoped styles.
    """

    template_name: str = ""
    component_name: str = ""
    scope: str = ""
    stylesheets: list[str] | None = None
    styles: str = ""
    scoped_styles: bool = True
    _prop_fields: ClassVar[dict[str, Prop]] = {}

    def __init__(
        self,
        *,
        instance_id: str | None = None,
        props: dict[str, Any] | None = None,
        state: dict[str, Any] | None = None,
        slots: dict[str, str] | None = None,
    ) -> None:
        self.instance_id = instance_id or uuid4().hex
        self._raw_props = props or {}
        self._props = self._resolve_props(self._raw_props)
        self._state = state if state is not None else self.get_initial_state()
        self._slots = SlotContent.from_mapping(slots)

    @classmethod
    def prop_names(cls) -> list[str]:
        return list(cls._prop_fields.keys())

    @classmethod
    def action_names(cls) -> list[str]:
        return [
            name
            for name in dir(cls)
            if name != "dispatch_action"
            and callable(getattr(cls, name))
            and getattr(getattr(cls, name), ACTION_MARKER, False)
        ]

    def get_initial_state(self) -> dict[str, Any]:
        return {}

    @property
    def shard_scope(self) -> str:
        return component_scope(self.component_name, self.scope)

    def get_context_data(self) -> dict[str, Any]:
        return {
            "component": self,
            "props": self.props,
            "state": self.state,
            "slots": self._slots.as_dict(),
            "shard_id": self.instance_id,
            "shard_scope": self.shard_scope,
            "shard_actions": self.action_urls(),
        }

    def render(self, request=None) -> SafeString:
        if not self.template_name:
            raise ValueError(f"{self.__class__.__name__} is missing template_name.")

        context = self.get_context_data()
        if request is not None:
            context["request"] = request

        html = render_to_string(self.template_name, context, request=request)
        styles = ""
        if self.scoped_styles:
            styles = load_scoped_styles(
                scope=self.shard_scope,
                template_name=self.template_name,
                stylesheets=self.stylesheets,
                inline_styles=self.styles,
            )

        return mark_safe(f"{styles}{html}")

    def dispatch_action(self, action_name: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        handler = getattr(type(self), action_name, None)
        if handler is None or not getattr(handler, ACTION_MARKER, False):
            raise ActionNotFoundError(
                f"Action '{action_name}' is not defined on {self.__class__.__name__}."
            )

        clean_payload = {
            key: value
            for key, value in (payload or {}).items()
            if key not in IGNORED_PAYLOAD_KEYS
        }
        next_state = handler(self, dict(self._state), **clean_payload)
        if next_state is None:
            return dict(self._state)
        return next_state

    def persist(self) -> None:
        StateStore.save(
            instance_id=self.instance_id,
            component_name=self.component_name,
            props=self._raw_props,
            state=self._state,
            slots=self._slots.as_dict(),
        )

    @classmethod
    def from_storage(cls, instance_id: str) -> Component:
        record = StateStore.load(instance_id)
        component_cls = cls.registry_get(record.component_name)
        return component_cls(
            instance_id=instance_id,
            props=record.props,
            state=record.state,
            slots=record.slots,
        )

    @classmethod
    def registry_get(cls, component_name: str) -> type[Component]:
        from shard.registry import get_component

        return get_component(component_name)

    def action_urls(self) -> dict[str, str]:
        from django.urls import reverse

        from shard.conf import get_setting

        namespace = get_setting("URL_NAMESPACE")
        return {
            name: reverse(f"{namespace}:action", args=[self.instance_id, name])
            for name in self.action_names()
        }

    @property
    def props(self) -> dict[str, Any]:
        return dict(self._props)

    @property
    def state(self) -> dict[str, Any]:
        return dict(self._state)

    @state.setter
    def state(self, value: dict[str, Any]) -> None:
        self._state = dict(value)

    @property
    def slots(self) -> dict[str, str]:
        return self._slots.as_dict()

    def _resolve_props(self, raw: dict[str, Any]) -> dict[str, Any]:
        resolved: dict[str, Any] = {}
        errors: list[str] = []

        for name, prop in self._prop_fields.items():
            try:
                resolved[name] = prop.resolve(raw.get(name))
            except PropValidationError as exc:
                errors.append(str(exc))

        for name in raw:
            if name not in self._prop_fields:
                errors.append(f"Unknown prop '{name}' for {self.__class__.__name__}.")

        if errors:
            raise PropValidationError("; ".join(errors))

        return resolved


class TemplateComponent(Component):
    """Component with an inline Django template string."""

    inline_template: str = ""

    def render(self, request=None) -> SafeString:
        if self.inline_template:
            template = Template(self.inline_template)
            context = Context(self.get_context_data())
            if request is not None:
                context["request"] = request
            return mark_safe(template.render(context))
        return super().render(request=request)
