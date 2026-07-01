from __future__ import annotations

from typing import Any

from django.conf import settings

from shard.conf import get_setting


def shard(request) -> dict[str, Any]:
    """Expose Shard settings to every template."""

    return {
        "SHARD": {
            "version": _framework_version(),
            "url_namespace": get_setting("URL_NAMESPACE"),
            "debug": getattr(settings, "DEBUG", False),
        }
    }


def _framework_version() -> str:
    try:
        from shard import __version__

        return __version__
    except Exception:
        return "0.0.0"
