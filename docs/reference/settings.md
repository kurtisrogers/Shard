# Settings

All Shard settings use the `SHARD_` prefix in Django settings.

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

When `True`, Shard imports `<app>.components` for every installed app at startup.

```python
SHARD_AUTODISCOVER = False  # manual registration only
```

## Context processor

Add `shard.context_processors.shard` to expose `SHARD` in templates:

```python
SHARD = {
    "version": "0.2.0",
    "url_namespace": "shard",
    "debug": True,
}
```

## Cache configuration

Shard uses Django's default cache. For production:

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

Run `python manage.py collectstatic` in production. Shard assets are under `shard/static/shard/`.
