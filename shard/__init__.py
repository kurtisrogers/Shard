"""Shard — a Django-native component framework."""

from shard.actions import ActionResult
from shard.component import Component, action, computed, emits
from shard.props import Prop
from shard.render import mount, render_component

__all__ = [
    "ActionResult",
    "Component",
    "Prop",
    "action",
    "computed",
    "emits",
    "mount",
    "render_component",
]

__version__ = "0.2.0"
