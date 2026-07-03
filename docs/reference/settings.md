# Settings

All Shrd settings use the `SHARD_` prefix in Django settings.

## SHARD_STATE_TIMEOUT

**Default:** `86400` (24 hours)

Seconds to keep component state (props, state, slots) in cache.

```python
SHARD_STATE_TIMEOUT = 60 * 30  # 30 minutes
```

## SHARD_URL_NAMESPACE

**Default:** `"shard"`

URL namespace for action routes. Must match your `include("shard.urls")` configuration.

```python
SHARD_URL_NAMESPACE = "shard"
```

## SHARD_AUTODISCOVER

**Default:** `True`

When `True`, Shrd imports `<app>.components` for every installed app at startup.

```python
SHARD_AUTODISCOVER = False  # manual registration only
```

## SHARD_LOAD_ALPINE

**Default:** `False`

When `True`, `{% shard_scripts %}` includes Alpine.js by default. Otherwise pass `alpine=True` per page:

```django
{% shard_scripts alpine=True %}
```

## SHARD_PRELOAD_SCRIPTS

**Default:** `True`

When `True`, `{% shard_scripts %}` emits `<link rel="preload" as="script">` hints for HTMX and `shard.js` (and Alpine when loaded). Disable if your CSP or asset pipeline handles preloading elsewhere:

```python
SHARD_PRELOAD_SCRIPTS = False
```

## SHARD_MINIFY_CSS

**Default:** `False` when `DEBUG=True`, otherwise `True`

When `True`, scoped component CSS is minified before injection. In development, CSS stays readable in DevTools unless you override:

```python
SHARD_MINIFY_CSS = True  # force minification in DEBUG
SHARD_MINIFY_CSS = False  # force readable CSS in production
```

## SHARD_VIEW_DATA_ALLOWED_COMPONENTS

**Default:** `None`

Optional global whitelist of component names allowed in [view data](../guides/view-data.md) trees. When `None`, you must pass `allowed_components=` to `render_view_data()` or set `allowed_view_components` on a `ViewTreeComponent` subclass.

```python
SHARD_VIEW_DATA_ALLOWED_COMPONENTS = [
    "Layout",
    "Card",
    "Counter",
]
```

For security, always restrict which components view data can instantiate. Never pass user-controlled component names without validation.

## Context processor

Add `shard.context_processors.shard` to expose `SHARD` in templates:

```python
SHARD = {
    "version": "0.3.0",
    "url_namespace": "shard",
    "debug": True,
}
```

## Cache configuration

Shrd uses Django's default cache. For production:

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/1"),
    }
}
```

## Static files

```python
STATIC_URL = "static/"
```

Run `python manage.py collectstatic` in production. Shrd assets are under `shard/static/shard/`.
