"""Spike: render Shard component trees from structured view data."""

from __future__ import annotations

from typing import Any, TypedDict

from django.utils.safestring import SafeString

from shard.exceptions import ComponentNotFoundError
from shard.registry import get_component
from shard.render import mount

ALLOWED_COMPONENTS = frozenset(
    {
        "Alert",
        "Button",
        "Card",
        "Counter",
        "Layout",
        "TodoList",
    }
)


class ViewDataError(ValueError):
    """Raised when view data is invalid or references a disallowed component."""


class ViewNode(TypedDict, total=False):
    component: str
    props: dict[str, Any]
    slots: dict[str, list[ViewNode]]
    children: list[ViewNode]
    content: str


DEMO_VIEW_DATA: ViewNode = {
    "component": "Layout",
    "slots": {
        "header": [
            {
                "component": "Alert",
                "props": {"level": "info", "message": "This page was built from view data."},
            }
        ],
        "default": [
            {
                "component": "Card",
                "props": {"title": "Counter"},
                "children": [
                    {"component": "Counter", "props": {"initial": 3, "step": 2}},
                ],
            },
            {
                "component": "Card",
                "props": {"title": "Todo list"},
                "children": [
                    {"component": "TodoList", "props": {"placeholder": "What needs doing?"}},
                ],
            },
            {
                "component": "Card",
                "props": {"title": "Wrapped actions"},
                "children": [
                    {
                        "component": "Button",
                        "props": {"variant": "primary"},
                        "content": "Primary action",
                    },
                    {
                        "component": "Button",
                        "props": {"variant": "ghost"},
                        "content": "Secondary action",
                    },
                ],
            },
        ],
        "footer": [
            {
                "component": "Alert",
                "props": {"level": "success", "message": "View-data spike — HTMX actions still work."},
            }
        ],
    },
}


def render_view_data(
    node: ViewNode,
    *,
    request=None,
    allowed_components: frozenset[str] | None = None,
) -> SafeString:
    """Walk a view-data tree and mount Shard components recursively."""

    return _render_node(
        node,
        request=request,
        allowed_components=allowed_components or ALLOWED_COMPONENTS,
    )


def _render_node(
    node: ViewNode,
    *,
    request,
    allowed_components: frozenset[str],
) -> SafeString:
    if not isinstance(node, dict):
        raise ViewDataError("Each view-data node must be a mapping.")

    component_name = node.get("component")
    if not component_name:
        raise ViewDataError("Each view-data node requires a 'component' name.")

    if component_name not in allowed_components:
        raise ViewDataError(f"Component '{component_name}' is not allowed in view data.")

    try:
        component_cls = get_component(component_name)
    except ComponentNotFoundError as exc:
        raise ViewDataError(str(exc)) from exc

    slots: dict[str, str] = {}
    for slot_name, child_nodes in (node.get("slots") or {}).items():
        if not isinstance(child_nodes, list):
            raise ViewDataError(f"Slot '{slot_name}' must be a list of child nodes.")
        slots[slot_name] = "".join(
            _render_node(child, request=request, allowed_components=allowed_components)
            for child in child_nodes
        )

    children = node.get("children") or []
    if children and not isinstance(children, list):
        raise ViewDataError("'children' must be a list of child nodes.")

    child_html = "".join(
        _render_node(child, request=request, allowed_components=allowed_components)
        for child in children
    )
    if child_html:
        slots["default"] = f"{slots.get('default', '')}{child_html}"

    content = node.get("content")
    if content:
        slots["default"] = f"{slots.get('default', '')}{content}"

    return mount(
        component_cls,
        props=node.get("props") or {},
        slots=slots or None,
        request=request,
    )
