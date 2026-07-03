# CLI

## shard_list

List all registered components:

```bash
python manage.py shard_list
python manage.py shard_list --verbose
```

`--verbose` adds template name, scope, scoped-styles flag, and warnings for missing templates.

## shard_doctor

Check project configuration and component health:

```bash
python manage.py shard_doctor
```

Verifies:

- Django cache is configured
- `SHARD_URL_NAMESPACE` reverses action URLs
- Registered components have `template_name` set
- Component templates resolve

Exits with code 1 when issues are found (suitable for CI smoke checks).

## shard_report

Report framework size and page-load weight:

```bash
python manage.py shard_report
python manage.py shard_report --json
python manage.py shard_report --check-budget
```

Shows raw and gzip sizes for bundled JS, request counts, Python package footprint, and optional CI size budgets.

Example `shard_list` output:

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
