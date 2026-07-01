# Testing

Shard uses **pytest** and **pytest-django** for its test suite.

## Run tests

```bash
pip install -e ".[dev]"
python -m pytest tests/ -q
```

## With coverage

```bash
python -m pytest tests/ --cov=shard --cov-report=term-missing
```

Current coverage: **~92%** of the `shard` package.

## Test layout

| File | What it covers |
|------|----------------|
| `test_props.py` | Prop validation, coercion, descriptors |
| `test_scoping.py` | CSS scoping engine |
| `test_state.py` | Cache persistence for props/state/slots |
| `test_component.py` | Actions, computed, hooks, events, nesting |
| `test_registry.py` | Component registration |
| `test_htmx.py` | HTMX and Alpine attribute builders |
| `test_templatetags.py` | Django template tags |
| `test_views.py` | HTTP endpoints and error responses |
| `test_styles.py` | Scoped stylesheet loading |
| `test_integration.py` | Example app end-to-end flows |

## Test settings

Tests use `tests/settings.py`, which extends the example project settings and adds `tests/templates/` to `TEMPLATES["DIRS"]`.

## Test components

Isolated components live in `tests/support/components.py` and are registered automatically via `tests/conftest.py`. They do not pollute the example application.

## CI

The `tests.yml` GitHub Actions workflow runs the full suite with coverage on every push and pull request.
