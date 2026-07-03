# Accessibility

Shrd can check rendered component HTML for common accessibility issues. This works for **static components** and **view-data trees** because both produce HTML before the check runs.

## Quick check

```bash
python manage.py shard_a11y
```

JSON output:

```bash
python manage.py shard_a11y --json
```

Optional static checks on template source files:

```bash
python manage.py shard_a11y path/to/components/card.html
```

## What gets checked

### Rendered output (recommended)

The command mounts registered components with sample props and renders configured view-data trees, then checks the HTML for issues such as:

| Code | Issue |
| ---- | ----- |
| `missing-alt` | `<img>` without an `alt` attribute |
| `missing-label` | Text inputs without `aria-label`, `aria-labelledby`, or associated label |
| `missing-name` | Buttons or links with no accessible name |
| `duplicate-id` | Duplicate `id` attributes in the same fragment |
| `positive-tabindex` | `tabindex` greater than 0 |
| `missing-lang` | Full documents missing `<html lang>` |

### View data

View-data layouts are checked **after rendering**:

```python
render_view_data(tree, allowed_components=..., stable=True)
```

The JSON tree is not scanned directly — the generated HTML is. That means dynamic layouts are covered as long as you include representative trees in your sample configuration.

## Configure samples for your project

Define render props for components:

```python
SHARD_A11Y_COMPONENT_SAMPLES = {
    "Counter": {"props": {"initial": 0, "step": 1}, "slots": {}},
    "Card": {
        "props": {"title": "Example"},
        "slots": {"default": "<p>Body</p>"},
    },
}
```

Define view-data trees to render:

```python
SHARD_A11Y_VIEW_DATA = [
    (
        "dashboard.layout",
        {"component": "Layout", "slots": {"default": [{"component": "Card", "props": {"title": "Hi"}}]}},
        frozenset({"Layout", "Card"}),
    ),
]
```

Each view-data entry is `(name, tree, allowed_components)`.

If unset, the example demo tree is used when the example app is installed.

## Pre-commit

This repository runs accessibility checks in pre-commit:

```yaml
- repo: local
  hooks:
    - id: shard-a11y
      name: Shrd accessibility
      entry: scripts/shard_a11y_precommit.sh
      language: system
      pass_filenames: true
      always_run: true
```

Copy `scripts/shard_a11y_precommit.sh` into your project (or call `python manage.py shard_a11y` directly) and set `DJANGO_SETTINGS_MODULE` to your settings module.

## Limits

This is a **fast heuristic checker**, not a replacement for axe, Lighthouse, or manual screen-reader testing. It catches common mistakes early but does not analyze color contrast, focus order in the full page, or client-side behavior after HTMX swaps.

Use it as a guardrail in development; run fuller audits before release.
