# Project setup

## Recommended layout

```
myproject/
├── myapp/
│   ├── components.py          # Component classes
│   ├── templates/
│   │   └── components/        # Component templates + CSS
│   │       ├── card.html
│   │       ├── card.css
│   │       ├── counter.html
│   │       └── counter.css
│   └── views.py
├── templates/
│   └── pages/                 # Full page templates
│       └── home.html
└── settings.py
```

## `components.py` convention

Each Django app can have a `components.py` module at the app root. Shard's autodiscover imports it at startup and registers every `Component` subclass defined there.

```python
# myapp/components.py
from shard import Component, Prop

class Card(Component):
    title = Prop(str, default="")
    template_name = "components/card.html"
```

You can also register components manually:

```python
from shard.registry import register
from .widgets import DatePicker

register(DatePicker, name="DatePicker")
```

## URL configuration

Shard needs a URL prefix for HTMX action endpoints:

```python
# urls.py
from django.urls import include, path

urlpatterns = [
    path("shard/", include("shard.urls")),
]
```

Actions are served at `/shard/action/<instance_id>/<action_name>/`.

## Template directories

Add your app's template directory to `TEMPLATES["DIRS"]` or use `APP_DIRS = True` (default). Component templates are regular Django templates — no special loader required.

## Settings reference

| Setting               | Default   | Description                              |
| --------------------- | --------- | ---------------------------------------- |
| `SHARD_STATE_TIMEOUT` | `86400`   | Seconds to keep component state in cache |
| `SHARD_URL_NAMESPACE` | `"shard"` | URL namespace for action routes          |
| `SHARD_AUTODISCOVER`  | `True`    | Import `<app>.components` on startup     |

## Verify installation

```bash
python manage.py shard_list
```

Lists all registered components with their props and actions.

## Test your components

Shard works with pytest and pytest-django. See the [Testing guide](../guides/testing.md) for settings, `conftest.py`, and examples using `mount()`, direct action tests, and HTMX client requests.
