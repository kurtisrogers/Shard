"""Render Shard component trees from structured view data."""

from __future__ import annotations

import copy
from typing import Any, TypedDict
from uuid import uuid4

from django.utils.safestring import SafeString

from shard.conf import get_setting
from shard.exceptions import ComponentNotFoundError, StateNotFoundError, ViewDataError
from shard.registry import get_component
from shard.state import StateStore

TREE_STATE_KEY = "tree"


class ViewNode(TypedDict, total=False):
    """Serializable descriptor for a component in a view-data tree."""

    id: str
    component: str
    props: dict[str, Any]
    slots: dict[str, list[ViewNode]]
    children: list[ViewNode]
    content: str


def resolve_allowed_components(
    *,
    allowed_components: frozenset[str] | None = None,
) -> frozenset[str]:
    """Resolve the component whitelist for view-data rendering."""

    if allowed_components is not None:
        return allowed_components

    configured = get_setting("VIEW_DATA_ALLOWED_COMPONENTS")
    if configured is None:
        raise ViewDataError(
            "View data rendering requires an explicit component whitelist. "
            "Pass allowed_components=... to render_view_data() or set "
            "SHARD_VIEW_DATA_ALLOWED_COMPONENTS in Django settings."
        )
    return frozenset(configured)


def ensure_node_ids(node: ViewNode) -> ViewNode:
    """Assign a stable ``id`` to every node that does not already have one."""

    node = copy.deepcopy(node)
    node.setdefault("id", uuid4().hex)

    slots = node.get("slots")
    if slots:
        node["slots"] = {
            slot_name: [ensure_node_ids(child) for child in children]
            for slot_name, children in slots.items()
        }

    children = node.get("children")
    if children:
        node["children"] = [ensure_node_ids(child) for child in children]

    return node


def collect_node_ids(node: ViewNode) -> set[str]:
    """Return every instance id referenced in a view-data tree."""

    ids: set[str] = set()
    _walk_node_ids(node, ids)
    return ids


def get_slot_nodes(tree: ViewNode, slot_name: str) -> list[ViewNode]:
    """Return the child nodes for a named slot on the tree root."""

    return list((tree.get("slots") or {}).get(slot_name, []))


def set_slot_nodes(tree: ViewNode, slot_name: str, nodes: list[ViewNode]) -> ViewNode:
    """Return a copy of ``tree`` with ``slot_name`` replaced."""

    updated = copy.deepcopy(tree)
    slots = dict(updated.get("slots") or {})
    slots[slot_name] = nodes
    updated["slots"] = slots
    return updated


def commit_view_tree(state: dict[str, Any], key: str, tree: ViewNode) -> ViewNode:
    """Replace a view tree in state and prune cache entries for removed nodes."""

    previous = state.get(key, {})
    previous_ids = collect_node_ids(previous) if previous else set()
    updated = ensure_node_ids(tree)
    prune_orphaned_nodes(previous_ids - collect_node_ids(updated))
    state[key] = updated
    return updated


def prune_orphaned_nodes(instance_ids: set[str]) -> None:
    """Delete persisted state for component instances removed from a view tree."""

    for instance_id in instance_ids:
        StateStore.delete(instance_id)


def render_view_data(
    node: ViewNode,
    *,
    request=None,
    allowed_components: frozenset[str] | None = None,
    stable: bool = False,
) -> SafeString:
    """Walk a view-data tree and mount Shard components recursively."""

    whitelist = resolve_allowed_components(allowed_components=allowed_components)
    return _render_node(
        node,
        request=request,
        allowed_components=whitelist,
        stable=stable,
    )


def _walk_node_ids(node: ViewNode, ids: set[str]) -> None:
    node_id = node.get("id")
    if node_id:
        ids.add(node_id)

    for child_nodes in (node.get("slots") or {}).values():
        for child in child_nodes:
            _walk_node_ids(child, ids)

    for child in node.get("children") or []:
        _walk_node_ids(child, ids)


def _mount_node(
    component_cls,
    *,
    instance_id: str,
    props: dict[str, Any],
    slots: dict[str, str] | None,
    request,
    stable: bool,
) -> SafeString:
    if stable:
        try:
            record = StateStore.load(instance_id)
            instance = component_cls(
                instance_id=instance_id,
                props=props,
                state=record.state,
                slots=slots or {},
            )
        except StateNotFoundError:
            instance = component_cls(
                instance_id=instance_id,
                props=props,
                slots=slots or {},
            )
    else:
        instance = component_cls(
            instance_id=instance_id,
            props=props,
            slots=slots or {},
        )

    instance.persist()
    return instance.render(request=request)


def _render_node(
    node: ViewNode,
    *,
    request,
    allowed_components: frozenset[str],
    stable: bool,
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
            _render_node(child, request=request, allowed_components=allowed_components, stable=stable)
            for child in child_nodes
        )

    children = node.get("children") or []
    if children and not isinstance(children, list):
        raise ViewDataError("'children' must be a list of child nodes.")

    child_html = "".join(
        _render_node(child, request=request, allowed_components=allowed_components, stable=stable)
        for child in children
    )
    if child_html:
        slots["default"] = f"{slots.get('default', '')}{child_html}"

    content = node.get("content")
    if content:
        slots["default"] = f"{slots.get('default', '')}{content}"

    instance_id = node.get("id") or uuid4().hex
    return _mount_node(
        component_cls,
        instance_id=instance_id,
        props=node.get("props") or {},
        slots=slots or None,
        request=request,
        stable=stable,
    )
