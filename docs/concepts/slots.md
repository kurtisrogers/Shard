# Slots

Slots let components wrap child content — the equivalent of React's `children` or Vue's `<slot>`.

## Default slot

Content between `{% component %}` and `{% endcomponent %}` becomes the default slot:

```django
{% component Card title="User profile" %}
  <p>This paragraph is passed into the card.</p>
{% endcomponent %}
```

```html
{# components/card.html #}
<article {% shard_root component %} class="card">
  <h2>{{ props.title }}</h2>
  <div class="card__body">{{ slots.default|safe }}</div>
</article>
```

Use `|safe` because slot content is pre-rendered HTML.

## Named slots

For layout components with multiple insertion points:

```django
{% component Layout %}
  {% slot header %}
    <h1>Dashboard</h1>
  {% endslot %}

  <p>Main content uses the default slot.</p>

  {% slot footer %}
    <small>© 2026</small>
  {% endslot %}
{% endcomponent %}
```

```html
{# components/layout.html #}
<div {% shard_root component %} class="layout">
  <header>{{ slots.header|default:""|safe }}</header>
  <main>{{ slots.default|safe }}</main>
  <footer>{{ slots.footer|default:""|safe }}</footer>
</div>
```

## Nesting components in slots

Slots can contain other components:

```django
{% component Card title="Counter" %}
  {% component Counter initial=3 %}{% endcomponent %}
{% endcomponent %}
```

Each nested component gets its own instance ID, state, and scoped styles.

## Slots are persisted

Slot HTML is saved to cache with the component instance. HTMX re-renders include the original slot content automatically — actions don't need to know about slots.

## Composition patterns

### Wrapper components

`Card`, `Button`, `Layout` — structural components that accept arbitrary content:

```python
class Button(Component):
    variant = Prop(str, default="default")
    template_name = "components/button.html"
```

### Leaf components

`Counter`, `TodoList` — self-contained components with state and actions. Usually placed inside wrappers, not the other way around.

### Slot-less components

Components without `{{ slots.* }}` in their template simply ignore wrapped content. Use self-closing syntax:

```django
{% component Counter initial=0 %}{% endcomponent %}
```

## Empty slots

Check before rendering:

```html
{% if slots.header %}
<header>{{ slots.header|safe }}</header>
{% endif %}
```

Or use the `default` filter: `{{ slots.header|default:"" }}`.
