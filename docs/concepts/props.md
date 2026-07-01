# Props

Props are typed inputs passed into a component, similar to React props or Vue props.

## Declaring props

```python
from shard import Component, Prop

class Button(Component):
    variant = Prop(str, default="default")
    disabled = Prop(bool, default=False)
    button_type = Prop(str, default="button")
    template_name = "components/button.html"
```

## Passing props in templates

```django
{% component Button variant="primary" button_type="submit" %}
  Save
{% endcomponent %}
```

## Prop options

```python
Prop(str)                        # optional string, default None
Prop(int, default=0)             # optional with default
Prop(str, required=True)         # must be provided
Prop(str, label="Display name")  # used in error messages
```

## Supported types

| Type | Coercion |
|------|----------|
| `str` | `str(value)` |
| `int` | `int(value)` |
| `float` | `float(value)` |
| `bool` | `"true"`, `"1"`, `"yes"` → `True` |
| `list[T]` | JSON array or Python list |

## Validation

Props are validated when a component is instantiated. Unknown props raise `PropValidationError`:

```python
# PropValidationError: Unknown prop 'colour' for Button.
{% component Button colour="red" %}{% endcomponent %}
```

## Accessing props

**In templates:**

```html
<button class="btn--{{ props.variant }}">
```

**In Python:**

```python
self.variant       # via descriptor
self.props         # full dict
self.props["variant"]
```

## Props vs state

| | Props | State |
|---|-------|-------|
| Set by | Parent / page template | `get_initial_state()` and `@action` |
| Mutable by component | No | Yes |
| Persisted across HTMX | Yes (frozen) | Yes (updated) |
| Use for | Configuration, labels, variants | Counters, form drafts, lists |

Props are inputs. State is internal data that changes over the component's lifetime.
