# Python API

## shard.Component

Base class for all components.

### Class attributes

- `template_name: str`
- `component_name: str`
- `scope: str`
- `stylesheets: list[str] | None`
- `styles: str`
- `scoped_styles: bool`

### Methods

| Method                                              | Description                |
| --------------------------------------------------- | -------------------------- |
| `get_initial_state()`                               | Return initial state dict  |
| `get_client_state()`                                | Return Alpine.js seed data |
| `get_context_data()`                                | Template context dict      |
| `get_computed_data()`                               | Computed values dict       |
| `render(request=None)`                              | Render component to HTML   |
| `render_child(component, props=, slots=, request=)` | Render nested component    |
| `dispatch_action(name, payload)`                    | Run action handler         |
| `persist()`                                         | Save to cache              |
| `action_urls()`                                     | Dict of action URLs        |
| `before_action(name, payload)`                      | Lifecycle hook             |
| `after_action(name, state)`                         | Lifecycle hook             |

### Properties

- `props` — resolved prop dict
- `state` — server state dict
- `slots` — slot content dict
- `shard_scope` — CSS scope key
- `instance_id` — unique instance ID
- `pending_events` — events from last action
- `pending_redirect` — redirect from last action

## shard.Prop

```python
Prop(type, default=None, required=False, label="")
```

## Decorators

```python
@action          # mark method as HTMX action
@computed        # expose method return in template context
@emits("event")  # declare HTMX events after action
```

## shard.ActionResult

```python
ActionResult(state=None, events={}, redirect=None)
ActionResult.with_events(state, **events)
```

## Render functions

```python
from shard import mount, mount_component, render_component
from shard.render import MountResult

html = mount(Counter, props={"initial": 5})
result = mount_component(Counter, props={"initial": 5})  # MountResult(html, instance_id, component)
html = render_component(Counter, props={"initial": 5}, slots={"default": "<p>Hi</p>"})
```

`mount()` returns HTML only. `mount_component()` returns a `MountResult` with `html`, `instance_id`, and the live `component` instance — useful in tests and dynamic layouts.

## Testing helpers

```python
from shard.testing import extract_instance_id, post_action

instance_id = extract_instance_id(html)
response = post_action(client, instance_id, "increment")
```

See the [Testing guide](../guides/testing.md) for full pytest setup.

## View data

Render component trees from structured data. See the [View data guide](../guides/view-data.md).

```python
from shard import (
    ViewTreeComponent,
    commit_view_tree,
    ensure_node_ids,
    get_slot_nodes,
    render_view_data,
    set_slot_nodes,
)

html = render_view_data(
    {"component": "Card", "props": {"title": "Hi"}},
    allowed_components=frozenset({"Card"}),
    stable=True,  # preserve child state across re-renders
)
```

### shard.ViewTreeComponent

Base class for components whose layout is stored as view data in `state["tree"]`.

| Class attribute           | Default          | Description                                                   |
| ------------------------- | ---------------- | ------------------------------------------------------------- |
| `view_tree_key`           | `"tree"`         | State key holding the descriptor                              |
| `content_context_key`     | `"content_html"` | Template variable for rendered tree                           |
| `allowed_view_components` | `None`           | Whitelist; falls back to `SHARD_VIEW_DATA_ALLOWED_COMPONENTS` |

| Method                             | Description                                               |
| ---------------------------------- | --------------------------------------------------------- |
| `get_view_tree()`                  | Return the current descriptor from state                  |
| `set_view_tree(tree)`              | Replace the descriptor in memory                          |
| `commit_view_tree(state, tree)`    | Replace tree in action state and prune removed node cache |
| `render_view_tree(tree, request=)` | Render a tree with stable ids                             |

Subclasses must set `template_name` and render `{{ content_html|safe }}` in the template.

## Registry

```python
from shard.registry import register, get_component, get_all_components

register(MyComponent, name="MyComponent")
cls = get_component("MyComponent")
all_components = get_all_components()
```

## Exceptions

All public exceptions are importable from `shard`:

```python
from shard import (
    ActionNotFoundError,
    ComponentNotFoundError,
    PropValidationError,
    ShardError,
    StateNotFoundError,
    ViewDataError,
)
```

- `ShardError` — base exception
- `ComponentNotFoundError` — includes registry suggestions when lookup fails
- `PropValidationError` — includes component name and prop label
- `ActionNotFoundError` — lists available actions
- `StateNotFoundError` — mentions cache expiry and mounting
- `ViewDataError` — invalid view data or disallowed component name
