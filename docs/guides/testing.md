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

## Test settings

Tests use `tests/settings.py`, which extends the example project settings and adds `tests/templates/` to `TEMPLATES["DIRS"]`.

## Test components

Isolated components live in `tests/support/components.py` and are registered automatically via `tests/conftest.py`. They do not pollute the example application.

## CI

The `ci.yml` GitHub Actions workflow runs on every push and pull request:

| Job | What it checks |
|-----|----------------|
| **pre-commit** | All hooks in `.pre-commit-config.yaml` |
| **lint** | `ruff check` and `ruff format --check` |
| **test** | pytest on Python 3.10, 3.11, 3.12 (≥90% coverage) |
| **docs** | `mkdocs build --strict` |

## Pre-commit

Install hooks locally so checks run before each commit:

```bash
pip install -e ".[dev]"
pre-commit install
```

Run manually against all files:

```bash
pre-commit run --all-files
```

Hooks include trailing whitespace, YAML/TOML validation, **Ruff** (lint + format), and **Prettier** (Markdown/YAML).
