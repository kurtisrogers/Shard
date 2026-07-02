# Lifecycle hooks

Components can hook into the action dispatch lifecycle.

## before_action

Called before the action handler runs:

```python
def before_action(self, action_name: str, payload: dict) -> None:
    if action_name == "delete" and not self.props.allow_delete:
        raise PermissionError("Delete not allowed")
```

Use for:

- Authorization checks
- Logging / analytics
- Input normalization

## after_action

Called after the handler returns and state is normalized:

```python
def after_action(self, action_name: str, state: dict) -> None:
    if action_name == "save":
        logger.info("Saved item %s", state.get("id"))
```

Use for:

- Side effects that shouldn't block the response
- Cache invalidation
- Audit trails

## Render lifecycle

Shrd does not currently expose `before_render` / `after_render` hooks. Override `render()` on your component subclass if you need custom render behavior:

```python
def render(self, request=None):
    html = super().render(request=request)
  # post-process html
    return html
```

## Instance lifecycle

```
__init__ → get_initial_state() → persist() → render()
```

On HTMX:

```
from_storage / cache load → dispatch_action() → persist() → render()
```

Component instances are not long-lived objects. Each request creates or reconstructs an instance from cache.
