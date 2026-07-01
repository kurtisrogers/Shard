from django.conf import settings

DEFAULTS = {
    "STATE_BACKEND": "cache",
    "STATE_TIMEOUT": 60 * 60 * 24,
    "URL_NAMESPACE": "shard",
    "AUTODISCOVER": True,
    "LOAD_ALPINE": False,
    "PRELOAD_SCRIPTS": True,
    "MINIFY_CSS": True,
}


def get_setting(name: str):
    return getattr(settings, f"SHARD_{name}", DEFAULTS[name])
