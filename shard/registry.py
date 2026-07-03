from __future__ import annotations

import difflib
import importlib
from typing import TYPE_CHECKING

from django.apps import apps

from shard.conf import get_setting
from shard.exceptions import ComponentNotFoundError

if TYPE_CHECKING:
    from shard.component import Component


_REGISTRY: dict[str, type[Component]] = {}


def register(component_cls: type[Component], *, name: str | None = None) -> type[Component]:
    component_name = name or component_cls.component_name or component_cls.__name__
    component_cls.component_name = component_name
    _REGISTRY[component_name] = component_cls
    return component_cls


def _format_component_not_found(name: str) -> str:
    registered = sorted(_REGISTRY)
    message = (
        f"Component '{name}' is not registered. "
        "Ensure the app is in INSTALLED_APPS and components are defined in "
        "<app>/components.py (not only imported there)."
    )
    if not registered:
        return f"{message} No components are currently registered."

    suggestions = difflib.get_close_matches(name, registered, n=3, cutoff=0.6)
    if suggestions:
        message += f" Did you mean: {', '.join(suggestions)}?"

    preview = ", ".join(registered[:8])
    if len(registered) > 8:
        preview += ", ..."
    return f"{message} ({len(registered)} registered: {preview})"


def get_component(name: str) -> type[Component]:
    if name not in _REGISTRY:
        raise ComponentNotFoundError(_format_component_not_found(name))
    return _REGISTRY[name]


def get_all_components() -> dict[str, type[Component]]:
    return dict(_REGISTRY)


def autodiscover_components() -> None:
    if not get_setting("AUTODISCOVER"):
        return

    for app_config in apps.get_app_configs():
        if app_config.name == "shard":
            continue
        try:
            module = importlib.import_module(f"{app_config.name}.components")
        except ModuleNotFoundError:
            continue

        for attr_name in dir(module):
            value = getattr(module, attr_name)
            if (
                isinstance(value, type)
                and issubclass(
                    value,
                    __import__("shard.component", fromlist=["Component"]).Component,
                )
                and value.__module__ == module.__name__
            ):
                register(value)
