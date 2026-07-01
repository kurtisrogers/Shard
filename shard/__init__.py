"""Shard — a Django-native component framework."""

from shard.component import Component, action
from shard.props import Prop
from shard.render import mount, render_component

__all__ = [
    "Component",
    "Prop",
    "action",
    "mount",
    "render_component",
]

__version__ = "0.1.0"
