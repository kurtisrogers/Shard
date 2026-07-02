# Installation

## Requirements

- Python 3.10+
- Django 4.2+

## Install from PyPI

```bash
pip install shrd
```

Requires Python 3.10+ and Django 4.2+. The import name is `shard`:

```python
INSTALLED_APPS = ["shard", ...]
```

## Install from source

```bash
git clone https://github.com/kurtisrogers/Shard.git
cd Shard
pip install -e .
```

## Development install

Includes pytest for running the test suite:

```bash
pip install -e ".[dev]"
```

## Add to a Django project

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "shard",
    "myapp",  # your app with components.py
]

urlpatterns = [
    # ...
    path("shard/", include("shard.urls")),
]
```

## Optional context processor

Expose framework metadata in every template:

```python
TEMPLATES = [{
    "OPTIONS": {
        "context_processors": [
            # ...
            "shard.context_processors.shard",
        ],
    },
}]
```

This adds a `SHARD` dict with `version`, `url_namespace`, and `debug`.

## Static files

Shard bundles HTMX and Alpine.js. Load them once per page:

```django
{% load shard %}
{% shard_scripts %}
```

In production, run `collectstatic` as usual. Shard assets live under `shard/static/shard/`.

## Cache backend

Component state (props, slots, server state) is stored in Django's cache framework. Configure any cache backend:

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}
```

For development, `LocMemCache` works fine.

## Testing your project

Shard components are plain Django Python classes — test them with **pytest** and **pytest-django**:

```bash
pip install pytest pytest-django
```

See the [Testing guide](../guides/testing.md) for a settings checklist, `conftest.py` examples, and patterns for `mount()`, action logic, and HTMX requests.

## Documentation site

Published docs: [kurtisrogers.github.io/Shard](https://kurtisrogers.github.io/Shard/)

The **Deploy documentation** workflow (`.github/workflows/docs.yml`) builds MkDocs and deploys via GitHub Actions on every push to `main`. In **Settings → Pages**, set the source to **GitHub Actions** (not the `gh-pages` branch).

Build locally:

```bash
pip install -e ".[docs]"
python -m mkdocs serve
```
