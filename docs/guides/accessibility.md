# Accessibility

Shrd checks rendered component HTML with **[axe-core](https://github.com/dequelabs/axe-core)**. This works for **static components** and **view-data trees** because both produce HTML before the check runs.

## Quick check

```bash
npm ci
python manage.py shard_a11y
```

JSON output:

```bash
python manage.py shard_a11y --json
```

## How axe fits view data

View-data layouts are checked **after rendering**:

```python
render_view_data(tree, allowed_components=..., stable=True)
# axe runs on the resulting HTML
```

The JSON tree is not scanned directly. Add representative trees to `SHARD_A11Y_VIEW_DATA` so axe sees your dynamic layouts.

## What axe checks

`shard_a11y` renders registered components and configured view-data samples, then runs axe via a small Node script (`scripts/axe_check.mjs`) using jsdom.

Default tags: `wcag2a`, `wcag2aa`, `best-practice`.

For **component fragments**, page-level landmark rules (`region`, duplicate `main`) are disabled because fragments are embedded in full pages at runtime. Color contrast is also disabled in jsdom.

Run full-page axe checks (including contrast and landmarks) against served pages before release.

## Configure samples for your project

Component render props:

```python
SHARD_A11Y_COMPONENT_SAMPLES = {
    "Counter": {"props": {"initial": 0, "step": 1}, "slots": {}},
    "Card": {
        "props": {"title": "Example"},
        "slots": {"default": "<p>Body</p>"},
    },
}
```

View-data trees:

```python
SHARD_A11Y_VIEW_DATA = [
    (
        "dashboard.layout",
        {"component": "Layout", "slots": {"default": [{"component": "Card", "props": {"title": "Hi"}}]}},
        frozenset({"Layout", "Card"}),
    ),
]
```

## Pre-commit

This repository runs axe in pre-commit:

```yaml
- repo: local
  hooks:
    - id: shard-a11y
      name: Shrd accessibility (axe)
      entry: scripts/shard_a11y_precommit.sh
      language: system
      pass_filenames: true
      always_run: true
```

Requirements:

- **Node.js** (`npm ci` installs `axe-core` + `jsdom`)
- **Python/Django** settings for rendering components

The hook runs `npm ci` automatically when `node_modules` is missing.

## Limits

axe via jsdom catches most markup and ARIA issues early. It does **not** replace:

- Color contrast in real browsers
- Focus order after HTMX swaps
- Screen reader testing

Use `shard_a11y` as a fast guardrail; run Lighthouse or `@axe-core/cli` against served pages before release.
