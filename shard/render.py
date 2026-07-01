from __future__ import annotations

from typing import Any

from django.http import HttpRequest
from django.utils.safestring import SafeString

from shard.component import Component
from shard.registry import get_component
from shard.state import StateStore


def render_component(
    component: type[Component] | Component,
    *,
    props: dict[str, Any] | None = None,
    slots: dict[str, str] | None = None,
    request: HttpRequest | None = None,
    persist: bool = True,
) -> SafeString:
    """Instantiate and render a component, optionally persisting its state."""

    if isinstance(component, Component):
        instance = component
    else:
        instance = component(props=props or {}, slots=slots)

    if persist:
        instance.persist()
    return instance.render(request=request)


def mount(
    component: type[Component],
    *,
    props: dict[str, Any] | None = None,
    slots: dict[str, str] | None = None,
    request: HttpRequest | None = None,
) -> SafeString:
    """Create a new component instance and render it."""

    return render_component(
        component,
        props=props,
        slots=slots,
        request=request,
        persist=True,
    )


def resolve_and_render(instance_id: str, *, request: HttpRequest | None = None) -> SafeString:
    record = StateStore.load(instance_id)
    component_cls = get_component(record.component_name)
    instance = component_cls(
        instance_id=instance_id,
        props=record.props,
        state=record.state,
        slots=record.slots,
    )
    return instance.render(request=request)
