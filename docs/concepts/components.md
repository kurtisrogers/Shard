# Components

A Shard component is a Python class that ties together props, optional server state, a template, and optional scoped CSS.

## Defining a component

```python
from shard import Component, Prop

class Alert(Component):
    message = Prop(str, required=True)
    level = Prop(str, default="info")
    template_name = "components/alert.html"
```

## Class attributes

| Attribute        | Purpose                                              |
| ---------------- | ---------------------------------------------------- |
| `template_name`  | Django template path (required)                      |
| `component_name` | Registry name (defaults to class name)               |
| `scope`          | Override scoped CSS key (defaults to component name) |
| `stylesheets`    | Explicit list of CSS template paths                  |
| `styles`         | Inline CSS string (alternative to `.css` file)       |
| `scoped_styles`  | Set `False` to disable auto-scoping                  |

## Template context

Every component template receives:

| Variable        | Type        | Description                     |
| --------------- | ----------- | ------------------------------- |
| `component`     | `Component` | The component instance          |
| `props`         | `dict`      | Resolved prop values            |
| `state`         | `dict`      | Current server state            |
| `computed`      | `dict`      | Values from `@computed` methods |
| `slots`         | `dict`      | Rendered slot HTML by name      |
| `shard_id`      | `str`       | Unique instance identifier      |
| `shard_scope`   | `str`       | CSS scope key                   |
| `shard_actions` | `dict`      | Action name → URL mapping       |

## Prop access in Python

Props are descriptors. Access them on `self` inside component methods:

```python
class Counter(Component):
    step = Prop(int, default=1)

    @action
    def increment(self, state):
        state["count"] += self.step  # self.step returns resolved prop
        return state
```

## Root element convention

Component templates that use Shard tags must load the library:

```django
{% load shard %}
<div {% shard_root component %} class="alert">
```

This outputs `id="shard-<instance_id>"` and `data-shard-scope="<scope>"`, which HTMX and scoped CSS rely on.

## Inline templates

For small components, use `TemplateComponent`:

```python
from shard import TemplateComponent

class Badge(TemplateComponent):
    label = Prop(str, default="")
    inline_template = "<span class='badge'>{{ props.label }}</span>"
```

## Registration

Components in `<app>/components.py` are auto-registered. Verify with:

```bash
python manage.py shard_list
```
