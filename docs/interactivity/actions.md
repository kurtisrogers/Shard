# Actions

Actions are server-side methods that update component state in response to HTMX requests.

## Defining actions

```python
from shard import action

class Counter(Component):
    @action
    def increment(self, state):
        state["count"] += 1
        return state
```

## Action signature

```python
@action
def my_action(self, state, field: str = ""):
    # self    — component instance (access props via self.prop_name)
    # state   — copy of current state dict
    # **kwargs — POST parameters from HTMX (excluding CSRF token)
    return state
```

Always return the updated state dict, or an `ActionResult` for advanced cases.

## Wiring in templates

Use the `shard_htmx` tag:

```html
<button {% shard_htmx component "increment" %}>+</button>
```

For full examples (Counter, TodoList, forms, debounced input), see [Working with HTMX and Alpine](../guides/htmx-and-alpine.md).

Or manually:

```html
<button
  hx-post="{{ shard_actions.increment }}"
  hx-target="#shard-{{ shard_id }}"
  hx-swap="outerHTML"
>
  +
</button>
```

## POST parameters

Form fields in the HTMX request are passed as keyword arguments:

```html
<input name="text" />
<button {% shard_htmx component "add_item" %}>Add</button>
```

```python
@action
def add_item(self, state, text: str = ""):
    if text.strip():
        state["items"].append(text.strip())
    return state
```

Pass extra values with the `shard_htmx` tag:

```html
{% shard_htmx component "remove_item" index=forloop.counter0 %}
```

## ActionResult

Return events or redirects alongside state:

```python
from shard import ActionResult, action

@action
def save(self, state):
    # ... save logic ...
    return ActionResult.with_events(
        state,
        **{"item:saved": {"id": state["id"]}}
    )
```

Or with a redirect:

```python
return ActionResult(
    state=state,
    redirect="/success/",
)
```

## Lifecycle hooks

```python
def before_action(self, action_name, payload):
    # runs before handler

def after_action(self, action_name, state):
    # runs after handler
```

## Error handling

- Unknown actions → HTTP 404
- Expired state → HTTP 404
- Non-HTMX requests → HTTP 400

## Security

Actions require:

- `POST` method
- `HX-Request` header
- Valid CSRF token (Django's CSRF middleware)

Shrd does not expose GET endpoints for state mutation.
