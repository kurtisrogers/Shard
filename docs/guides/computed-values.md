# Computed values

Computed values are derived from props and state, exposed to templates without storing them in state.

## Defining computed values

```python
from shard import Component, computed

class Counter(Component):
    @computed
    def label(self) -> str:
        return f"Count is {self.state['count']}"
```

## Using in templates

```html
<p>{{ computed.label }}</p>
```

Computed values are recalculated on every render. They are not persisted.

## When to use computed

| Use computed | Use state |
|--------------|-----------|
| Formatted display strings | Values that change via actions |
| CSS class names from props | Lists, counters, drafts |
| Derived booleans | Anything HTMX actions modify |

## Example: dynamic CSS class

```python
class Alert(Component):
    level = Prop(str, default="info")

    @computed
    def css_class(self) -> str:
        return f"alert alert--{self.level}"
```

```html
<div class="{{ computed.css_class }}">{{ props.message }}</div>
```

## Access in computed methods

- `self.props` / `self.prop_name` — resolved props
- `self.state` — current server state
- `self.slots` — slot content (rarely needed in computed)

## Performance

Computed methods run synchronously during render. Keep them cheap — no database queries or external API calls. For heavy derivation, compute in `@action` and store in state.
