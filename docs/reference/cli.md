# CLI

## shard_list

List all registered components:

```bash
python manage.py shard_list
```

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
