"""Shard — a Django-native component framework."""

from shard.actions import ActionResult
from shard.component import Component, TemplateComponent, action, computed, emits
from shard.exceptions import (
    ActionNotFoundError,
    ComponentNotFoundError,
    PropValidationError,
    ShardError,
    StateNotFoundError,
)
from shard.props import Prop
from shard.render import MountResult, mount, mount_component, render_component

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
    "action",
    "computed",
    "emits",
    "mount",
    "mount_component",
    "render_component",
]

__version__ = "0.2.0"
