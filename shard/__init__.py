"""Shrd — a Django-native component framework."""

from shard.actions import ActionResult
from shard.component import Component, action, computed, emits
from shard.props import Prop
from shard.render import mount, render_component
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
    "ActionResult",
    "Component",
    "Prop",
    "ViewNode",
    "ViewTreeComponent",
    "action",
    "commit_view_tree",
    "computed",
    "emits",
    "ensure_node_ids",
    "get_slot_nodes",
    "mount",
    "render_component",
    "render_view_data",
    "set_slot_nodes",
]

__version__ = "0.3.0"
