# Testing

Shard works well with **pytest** and **pytest-django**. You do not need a browser, Selenium, or a JavaScript test runner — components render server-side and actions are plain HTTP requests.

This guide covers testing **your Django project** that uses Shard. For running the Shard framework's own test suite, see [Framework development](#framework-development) at the bottom.

## Prerequisites

Before writing tests, confirm your project has the same pieces Shard needs at runtime:

| Requirement                             | Why                                                               |
| --------------------------------------- | ----------------------------------------------------------------- |
| `"shard"` in `INSTALLED_APPS`           | Registers the app and autodiscovers components                    |
| `path("shard/", include("shard.urls"))` | HTMX action and render endpoints                                  |
| `CACHES` configured                     | Component state (props, state, slots) is stored in Django's cache |
| `DJANGO_SETTINGS_MODULE` for pytest     | pytest-django needs your settings module                          |

Example cache for tests (in-memory is fine):

```python
# settings.py or settings/test.py
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
```

If your URL namespace is not `"shard"`, set `SHARD_URL_NAMESPACE` to match your `include()` name and use that prefix in test URLs.

## Install test dependencies

In your project:

```bash
pip install pytest pytest-django
```

You do **not** need Shard's development extras unless you are contributing to the framework itself.

## pytest configuration

Add to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "myproject.settings"
pythonpath = ["."]
testpaths = ["tests"]
```

Or use `pytest.ini`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = myproject.settings
pythonpath = .
testpaths = tests
```

## Recommended `conftest.py`

Create `tests/conftest.py` in your project:

```python
import pytest

from myapp.components import Counter  # only if you disable autodiscover


@pytest.fixture
def shard_instance_id():
    """Extract a mounted component's instance ID from rendered HTML."""

    def _extract(html: str) -> str:
        return html.split('id="shard-')[1].split('"')[0]

    return _extract


@pytest.fixture(autouse=True)
def clear_shard_cache():
    """Optional: reset cache between tests if you reuse instance IDs."""
    from django.core.cache import cache

    cache.clear()
    yield
    cache.clear()
```

### Component registration

With `SHARD_AUTODISCOVER = True` (the default), components in `<app>.components` are registered automatically — no extra fixture needed.

If autodiscover is disabled, register components in `conftest.py`:

```python
import pytest

from shard.registry import register
from myapp.components import Counter, Card


@pytest.fixture(autouse=True)
def register_components():
    for cls in (Counter, Card):
        register(cls)
    yield
```

## Three ways to test

### 1. Render HTML with `mount()`

Fastest way to test templates, props, slots, scoped CSS, and computed values. No HTTP required.

```python
from shard import mount

from myapp.components import Counter, Card


def test_counter_renders_initial_count():
    html = mount(Counter, props={"initial": 5, "step": 1})
    assert "Current count is 5" in html
    assert 'data-shard-scope="counter"' in html


def test_card_renders_slot_content():
    html = mount(
        Card,
        props={"title": "Hello"},
        slots={"default": "<p>World</p>"},
    )
    assert "Hello" in html
    assert "<p>World</p>" in html
```

`mount()` creates a new instance (random ID), persists state to cache, and returns rendered HTML — the same path production uses on first render.

Use `render_component()` when you need more control (e.g. `persist=False` for pure snapshot tests).

### 2. Test action logic directly

Call `dispatch_action()` on a component instance to test server logic without routing or HTMX headers.

```python
import pytest

from shard.exceptions import ActionNotFoundError
from myapp.components import Counter


def test_increment_updates_state():
    component = Counter(props={"initial": 0, "step": 2})
    new_state = component.dispatch_action("increment", {})
    assert new_state["count"] == 2


def test_unknown_action_raises():
    component = Counter(props={"initial": 0, "step": 1})
    with pytest.raises(ActionNotFoundError):
        component.dispatch_action("not_real", {})
```

Also useful for lifecycle hooks (`before_action`, `after_action`), `@computed` methods, and `ActionResult` with events or redirects.

### 3. Test HTMX endpoints with Django's test client

Integration tests that exercise the full request cycle: URL routing, cache load/save, response headers, and HTML fragments.

```python
import json

import pytest
from django.test import Client

from shard import mount

from myapp.components import Counter


@pytest.fixture
def client():
    return Client()


def test_increment_action_via_htmx(client, shard_instance_id):
    html = mount(Counter, props={"initial": 1, "step": 2})
    instance_id = shard_instance_id(html)

    response = client.post(
        f"/shard/action/{instance_id}/increment/",
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert "Current count is 3" in response.content.decode()

    events = json.loads(response["HX-Trigger"])
    assert events["counter:changed"] is True
    assert events["shard:action-complete"] is True
```

Important details:

- Set `HTTP_HX_REQUEST="true"` — Shard rejects non-HTMX action requests with **400**
- Mount the component first so state exists in cache before posting to the action URL
- Parse `HX-Trigger` to assert `@emits` events

Test the render endpoint the same way:

```python
def test_render_endpoint_returns_fresh_html(client, shard_instance_id):
    html = mount(Counter, props={"initial": 7, "step": 1})
    instance_id = shard_instance_id(html)

    response = client.get(f"/shard/render/{instance_id}/")

    assert response.status_code == 200
    assert "Current count is 7" in response.content.decode()
```

## Testing pages and template tags

Full pages that use `{% component %}` can be tested with the Django client:

```python
def test_home_page_renders_components(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Primary action" in response.content.decode()
```

Template tags (`{% shard_scripts %}`, `{% shard_htmx %}`, etc.) can be tested with Django's template engine:

```python
from django.template import Context, Template


def test_shard_scripts_includes_htmx():
    template = Template("{% load shard %}{% shard_scripts %}")
    html = template.render(Context({}))
    assert "htmx.min.js" in html
```

## Testing prop validation

Invalid props raise `PropValidationError` at instantiation:

```python
import pytest

from shard.exceptions import PropValidationError
from myapp.components import Counter


def test_invalid_prop_type_raises():
    with pytest.raises(PropValidationError):
        Counter(props={"initial": "not-a-number", "step": 1})
```

## What you usually do not need

| Often unnecessary        | Why                                          |
| ------------------------ | -------------------------------------------- |
| `@pytest.mark.django_db` | Shard state lives in cache, not the database |
| Browser / Playwright     | No client-side framework to hydrate          |
| Mocking HTMX             | Post to Django URLs with `HTTP_HX_REQUEST`   |
| Separate frontend build  | Templates render server-side in tests        |

Add `django_db` only when your components or views touch the ORM.

## Tips

1. **Extract instance IDs** with a small helper (see `shard_instance_id` fixture above) or a one-liner: `html.split('id="shard-')[1].split('"')[0]`
2. **Slots survive actions** — cache stores slot HTML; re-render endpoints should still include slot content
3. **HTMX partials omit scoped CSS** — assert `"<style data-shard-styles="` is absent on action responses if you test partial swaps
4. **Isolate tests** — each `mount()` gets a new UUID; use `cache.clear()` if you construct components with fixed `instance_id`
5. **List registered components** — `python manage.py shard_list` helps verify autodiscover during setup

## Example test layout

```
myproject/
├── myapp/
│   └── components.py
└── tests/
    ├── conftest.py
    ├── test_components.py      # mount() and dispatch_action()
    ├── test_htmx_actions.py    # client.post to /shard/action/...
    └── test_pages.py           # full page responses
```

---

## Framework development

This section is for contributors working on the Shard package itself.

### Run the framework test suite

```bash
pip install -e ".[dev]"
python -m pytest tests/ -q
```

### With coverage

```bash
python -m pytest tests/ --cov=shard --cov-report=term-missing
```

Current coverage: **~93%** of the `shard` package (≥90% enforced in CI).

### Test layout

| File                   | What it covers                            |
| ---------------------- | ----------------------------------------- |
| `test_props.py`        | Prop validation, coercion, descriptors    |
| `test_scoping.py`      | CSS scoping engine                        |
| `test_state.py`        | Cache persistence for props/state/slots   |
| `test_component.py`    | Actions, computed, hooks, events, nesting |
| `test_registry.py`     | Component registration                    |
| `test_htmx.py`         | HTMX and Alpine attribute builders        |
| `test_templatetags.py` | Django template tags                      |
| `test_views.py`        | HTTP endpoints and error responses        |
| `test_styles.py`       | Scoped stylesheet loading                 |
| `test_integration.py`  | Example app end-to-end flows              |

Framework tests use `tests/settings.py`, which extends the example project settings and adds `tests/templates/` to `TEMPLATES["DIRS"]`. Isolated test components live in `tests/support/components.py` and are registered via `tests/conftest.py`.

### CI

The `ci.yml` workflow runs pre-commit, Ruff, pytest (Python 3.10–3.12, ≥90% coverage), size budgets, and docs build on every pull request.
