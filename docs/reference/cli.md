# CLI

## shard_list

List all registered components:

```bash
python manage.py shard_list
```

## shard_report

Report framework size and page-load weight:

```bash
python manage.py shard_report
python manage.py shard_report --json
python manage.py shard_report --check-budget
```

Shows raw and gzip sizes for bundled JS, request counts, Python package footprint, and optional CI size budgets.

Output:

```
NAME       CLASS
--------------------------
Alert      example.components.Alert
  props: message, level
  actions: —
Button     example.components.Button
  props: variant, button_type
  actions: —
Counter    example.components.Counter
  props: initial, step
  actions: increment, decrement
```

Useful for verifying autodiscover and debugging registration issues.
