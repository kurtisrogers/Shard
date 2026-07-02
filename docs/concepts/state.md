# State

Server state is a dictionary owned by a component instance, persisted in Django's cache between HTMX requests.

## Initial state

Override `get_initial_state()` to set defaults:

```python
class Counter(Component):
    initial = Prop(int, default=0)

    def get_initial_state(self):
        return {"count": self.initial}
```

Props can seed initial state, but state itself is mutable.

## Reading state in templates

```html
<p>Count: {{ state.count }}</p>

{% if state.items %}
<ul>
  {% for item in state.items %}
  <li>{{ item }}</li>
  {% endfor %}
</ul>
{% endif %}
```

## Updating state with actions

State changes happen in `@action` methods. Return the updated state dict:

```python
@action
def increment(self, state):
    state["count"] += 1
    return state
```

Shrd persists the returned dict and re-renders the component.

## State persistence

Each component instance has a unique `shard_id`. State is stored in cache:

```
shard:state:<instance_id> → { component_name, props, state, slots }
```

Configure timeout via `SHARD_STATE_TIMEOUT` (default 24 hours).

## State lifecycle

```
Mount → get_initial_state() → persist → render
  ↓
HTMX action → load state → @action → save state → render
  ↓
(cache expiry) → instance lost
```

Expired state returns HTTP 404 on the next action. Design components so this is acceptable, or increase the timeout.

## Client state (Alpine.js)

For UI-only state (toggles, focus, animations), use Alpine.js via `get_client_state()`:

```python
def get_client_state(self):
    return {"open": False}
```

```html
<div {% shard_alpine component %}>
  <button @click="open = !open">Toggle</button>
  <div x-show="open">Panel</div>
</div>
```

Keep server state for data that must survive HTMX round-trips. Use client state for ephemeral UI on a single component.

For shared UI across components or the whole page, see [Shared and global client state](../guides/htmx-and-alpine.md#shared-and-global-client-state). Shrd does not provide a framework global Alpine store — use HTMX events, parent `x-data`, or `Alpine.store()` in your app.

## Slots in state

Slot HTML is persisted alongside state. When HTMX re-renders a component, wrapped content is preserved. You don't need to re-pass slots on each action.
