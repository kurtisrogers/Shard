from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from django.conf import settings

if TYPE_CHECKING:
    from shard.component import Component


def warn_missing_action(component: Component, action_name: str, *, source: str) -> None:
    if not getattr(settings, "DEBUG", False):
        return

    available = ", ".join(component.action_names()) or "(none)"
    warnings.warn(
        f"Shard: action '{action_name}' not found on {component.__class__.__name__} "
        f"({source}). Available actions: {available}.",
        stacklevel=3,
    )
