from __future__ import annotations

from functools import wraps
from typing import Any, Callable, ClassVar
from uuid import uuid4

from django.template import Context, Template
from django.template.loader import render_to_string
from django.utils.safestring import SafeString, mark_safe

from shard.actions import ActionResult
from shard.exceptions import ActionNotFoundError, PropValidationError
from shard.props import Prop
from shard.slots import SlotContent
from shard.state import StateStore
from shard.styles import component_scope, load_scoped_styles


ACTION_MARKER = "__shard_action__"
COMPUTED_MARKER = "__shard_computed__"
EMITS_MARKER = "__shard_emits__"
IGNORED_PAYLOAD_KEYS = frozenset({"csrfmiddlewaretoken", "shard"})


def action(method: Callable) -> Callable:
    """Mark a component method as an HTMX-callable server action."""

    @wraps(method)
    def wrapper(self, state: dict[str, Any], *args, **kwargs) -> Any:
        return method(self, state, *args, **kwargs)

    setattr(wrapper, ACTION_MARKER, True)
    if hasattr(method, EMITS_MARKER):
        setattr(wrapper, EMITS_MARKER, getattr(method, EMITS_MARKER))
    return wrapper


def computed(method: Callable) -> Callable:
    """Expose a method's return value as ``computed.<name>`` in templates."""

    @wraps(method)
    def wrapper(self) -> Any:
        return method(self)

    setattr(wrapper, COMPUTED_MARKER, True)
    return wrapper


def emits(*event_names: str) -> Callable:
    """Declare HTMX events fired after an action completes."""

    def decorator(method: Callable) -> Callable:
        setattr(method, EMITS_MARKER, tuple(event_names))
        return method

    return decorator


class ComponentMeta(type):
    def __new__(mcs, name: str, bases: tuple[type, ...], namespace: dict[str, Any]):
        prop_fields: dict[str, Prop] = {}
        computed_fields: dict[str, Callable] = {}

        for base in reversed(bases):
            prop_fields.update(getattr(base, "_prop_fields", {}))
            computed_fields.update(getattr(base, "_computed_fields", {}))

        for key, value in list(namespace.items()):
            if isinstance(value, Prop):
                prop_fields[key] = value.bind(key)
                namespace[key] = prop_fields[key]
            elif callable(value) and getattr(value, COMPUTED_MARKER, False):
                computed_fields[key] = value

        cls = super().__new__(mcs, name, bases, namespace)
        cls._prop_fields = prop_fields
        cls._computed_fields = computed_fields
        cls.component_name = namespace.get("component_name", name)
        return cls


class Component(metaclass=ComponentMeta):
    """Base class for Shard components."""

    template_name: str = ""
    component_name: str = ""
    scope: str = ""
    stylesheets: list[str] | None = None
    styles: str = ""
    scoped_styles: bool = True
    _prop_fields: ClassVar[dict[str, Prop]] = {}
    _computed_fields: ClassVar[dict[str, Callable]] = {}

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
        self._pending_events: dict[str, Any] = {}

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

    def get_client_state(self) -> dict[str, Any]:
        """Optional Alpine.js state. Override to seed ``x-data``."""

        return {}

    def before_action(self, action_name: str, payload: dict[str, Any]) -> None:
        """Hook called before an action handler runs."""

    def after_action(self, action_name: str, state: dict[str, Any]) -> None:
        """Hook called after an action handler runs."""

    @property
    def shard_scope(self) -> str:
        return component_scope(self.component_name, self.scope)

    def get_computed_data(self) -> dict[str, Any]:
        return {
            name: method(self)
            for name, method in type(self)._computed_fields.items()
        }

    def get_context_data(self) -> dict[str, Any]:
        return {
            "component": self,
            "props": self.props,
            "state": self.state,
            "computed": self.get_computed_data(),
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

    def render_child(
        self,
        component: type[Component] | str,
        *,
        props: dict[str, Any] | None = None,
        slots: dict[str, str] | None = None,
        request=None,
    ) -> SafeString:
        """Render a nested child component from Python or templates."""

        from shard.render import render_component
        from shard.registry import get_component

        component_cls = get_component(component) if isinstance(component, str) else component
        return render_component(
            component_cls,
            props=props,
            slots=slots,
            request=request,
            persist=True,
        )

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

        self.before_action(action_name, clean_payload)
        raw_result = handler(self, dict(self._state), **clean_payload)
        next_state, events, redirect = self._normalize_action_result(raw_result)

        declared_events = getattr(handler, EMITS_MARKER, ())
        for event_name in declared_events:
            events.setdefault(event_name, True)

        self._pending_events = events
        self._pending_redirect = redirect
        self.after_action(action_name, next_state)
        return next_state

    @property
    def pending_events(self) -> dict[str, Any]:
        return dict(self._pending_events)

    @property
    def pending_redirect(self) -> str | None:
        return getattr(self, "_pending_redirect", None)

    def _normalize_action_result(
        self,
        raw_result: Any,
    ) -> tuple[dict[str, Any], dict[str, Any], str | None]:
        if isinstance(raw_result, ActionResult):
            state = raw_result.state if raw_result.state is not None else dict(self._state)
            return state, dict(raw_result.events), raw_result.redirect

        if raw_result is None:
            return dict(self._state), {}, None

        if isinstance(raw_result, dict):
            return raw_result, {}, None

        raise TypeError(
            f"Action handlers must return a state dict or ActionResult, not {type(raw_result)!r}."
        )

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
