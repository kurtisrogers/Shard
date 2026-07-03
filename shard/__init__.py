"""Shrd — a Django-native component framework."""

from shard.actions import ActionResult
from shard.component import Component, TemplateComponent, action, computed, emits
from shard.exceptions import (
    ActionNotFoundError,
    ComponentNotFoundError,
    PropValidationError,
    ShardError,
    StateNotFoundError,
    ViewDataError,
)
from shard.props import Prop
from shard.render import MountResult, mount, mount_component, render_component
from shard.view_data import (
    ViewNode,
    commit_view_tree,
    ensure_node_ids,
    get_slot_nodes,
    render_view_data,
    set_slot_nodes,
)
from shard.view_tree import ViewTreeComponent

__all__ = [
    "ActionNotFoundError",
    "ActionResult",
    "Component",
    "ComponentNotFoundError",
    "MountResult",
    "Prop",
    "PropValidationError",
    "ShardError",
    "StateNotFoundError",
    "TemplateComponent",
    "ViewDataError",
    "ViewNode",
    "ViewTreeComponent",
    "action",
    "commit_view_tree",
    "computed",
    "emits",
    "ensure_node_ids",
    "get_slot_nodes",
    "mount",
    "mount_component",
    "render_component",
    "render_view_data",
    "set_slot_nodes",
]

__version__ = "0.3.0"
