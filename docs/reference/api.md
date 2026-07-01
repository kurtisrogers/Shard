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

| Method | Description |
|--------|-------------|
| `get_initial_state()` | Return initial state dict |
| `get_client_state()` | Return Alpine.js seed data |
| `get_context_data()` | Template context dict |
| `get_computed_data()` | Computed values dict |
| `render(request=None)` | Render component to HTML |
| `render_child(component, props=, slots=, request=)` | Render nested component |
| `dispatch_action(name, payload)` | Run action handler |
| `persist()` | Save to cache |
| `action_urls()` | Dict of action URLs |
| `before_action(name, payload)` | Lifecycle hook |
| `after_action(name, state)` | Lifecycle hook |

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
from shard import mount, render_component

html = mount(Counter, props={"initial": 5})
html = render_component(Counter, props={"initial": 5}, slots={"default": "<p>Hi</p>"})
```

## Registry

```python
from shard.registry import register, get_component, get_all_components

register(MyComponent, name="MyComponent")
cls = get_component("MyComponent")
all_components = get_all_components()
```

## Exceptions

- `ShardError` — base exception
- `ComponentNotFoundError`
- `PropValidationError`
- `ActionNotFoundError`
- `StateNotFoundError`
