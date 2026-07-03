from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from django.utils.html import escape
from django.utils.safestring import SafeString, mark_safe

from shard.debug import warn_missing_action

if TYPE_CHECKING:
    from shard.component import Component


def build_htmx_attrs(
    component: Component,
    action: str,
    *,
    swap: str = "outerHTML",
    target: str | None = None,
    trigger: str | None = None,
    vals: dict[str, Any] | None = None,
    include: str | None = None,
) -> SafeString:
    """Build HTMX attributes for a component action."""

    url = component.action_urls().get(action)
    if not url:
        warn_missing_action(component, action, source="shard_htmx")
        return mark_safe("")

    target_id = target or f"#shard-{component.instance_id}"
    attrs: list[str] = [
        f'hx-post="{escape(url)}"',
        f'hx-target="{escape(target_id)}"',
        f'hx-swap="{escape(swap)}"',
    ]

    if trigger:
        attrs.append(f'hx-trigger="{escape(trigger)}"')
    if include:
        attrs.append(f'hx-include="{escape(include)}"')
    if vals:
        attrs.append(f"hx-vals='{escape(json.dumps(vals))}'")

    return mark_safe(" ".join(attrs))


def build_alpine_data(component: Component, extra: dict[str, Any] | None = None) -> SafeString:
    """Serialize ``get_client_state()`` for an Alpine.js ``x-data`` attribute."""

    data: dict[str, Any] = {}
    if hasattr(component, "get_client_state"):
        data.update(component.get_client_state())
    if extra:
        data.update(extra)

    payload = json.dumps(data)
    return mark_safe(f"x-data='{escape(payload)}'")
