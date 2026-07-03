from __future__ import annotations

from typing import Any, Literal

from django.conf import settings

SettingName = Literal[
    "STATE_TIMEOUT",
    "URL_NAMESPACE",
    "AUTODISCOVER",
    "LOAD_ALPINE",
    "PRELOAD_SCRIPTS",
    "MINIFY_CSS",
    "VIEW_DATA_ALLOWED_COMPONENTS",
]

DEFAULTS: dict[SettingName, Any] = {
    "STATE_TIMEOUT": 60 * 60 * 24,
    "URL_NAMESPACE": "shard",
    "AUTODISCOVER": True,
    "LOAD_ALPINE": False,
    "PRELOAD_SCRIPTS": True,
    "VIEW_DATA_ALLOWED_COMPONENTS": None,
}


def get_setting(name: SettingName) -> Any:
    setting_attr = f"SHARD_{name}"
    if hasattr(settings, setting_attr):
        return getattr(settings, setting_attr)
    if name == "MINIFY_CSS":
        return not getattr(settings, "DEBUG", False)
    return DEFAULTS[name]
