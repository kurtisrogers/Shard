# Composition

Shard components compose through slots and nesting.

## Wrapper + leaf pattern

```django
{% component Card title="Tasks" %}
  {% component TodoList placeholder="Add a task" %}{% endcomponent %}
{% endcomponent %}
```

- **Wrapper** (`Card`) — provides structure and scoped styles, accepts slots
- **Leaf** (`TodoList`) — owns state and actions

## Layout components

Multi-slot layouts organize page structure:

```django
{% component Layout %}
  {% slot header %}<h1>Settings</h1>{% endslot %}
  <form>...</form>
  {% slot footer %}<button>Save</button>{% endslot %}
{% endcomponent %}
```

## Rendering children from Python

Inside a component method or template:

```python
# Python
html = self.render_child("Counter", props={"initial": 5})
```

```django
{# Template #}
{% shard_child "Counter" initial=5 %}
```

## When to nest where

| Approach | Best for |
|----------|----------|
| Slots in page template | Page-specific composition |
| `{% shard_child %}` in component template | Fixed child structure |
| `render_child()` in Python | Dynamic children based on props/state |

## Avoiding deep nesting

Three levels is usually enough:

```
Layout → Card → Counter
```

Deeper nesting works but makes slot content harder to reason about. Consider flattening or using page templates for complex layouts.

## Shared styles

Each component scopes its own CSS. Wrappers don't style slot content unless you use deep selectors (avoid this). Let leaf components own their appearance.

## Props drilling

Pass props explicitly at each level:

```django
{% component Card title="Counter" %}
  {% component Counter initial=3 step=2 %}{% endcomponent %}
{% endcomponent %}
```

There's no automatic prop forwarding. This keeps data flow explicit and debuggable.
