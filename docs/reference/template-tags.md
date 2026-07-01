# Template tags

Load with `{% load shard %}`.

## shard_scripts

Include HTMX, Alpine.js, and Shard glue scripts. Place once per page, typically in `<head>` or before `</body>`.

```django
{% shard_scripts %}
```

## component / endcomponent

Render a component with optional slot content.

```django
{% component Card title="Hello" %}
  <p>Slot content</p>
{% endcomponent %}
```

Self-closing (no slot content):

```django
{% component Counter initial=0 %}{% endcomponent %}
```

## slot / endslot

Named slot inside a component block.

```django
{% component Layout %}
  {% slot header %}<h1>Title</h1>{% endslot %}
  Main content
{% endcomponent %}
```

## shard_root

Root element attributes for a component instance.

```html
<div {% shard_root component %}>
```

Outputs: `id="shard-<id>" data-shard-scope="<scope>"`

## shard_action

URL for a specific action.

```html
<form action="{% shard_action component 'save' %}">
```

Prefer `shard_htmx` for most cases.

## shard_htmx

Generate HTMX attributes for an action.

```html
<button {% shard_htmx component "increment" %}>+</button>
<button {% shard_htmx component "search" trigger="keyup changed delay:300ms" swap="innerHTML" %}> 
<button {% shard_htmx component "remove" index=forloop.counter0 %}>
```

## shard_alpine

Generate Alpine.js `x-data` from `get_client_state()`.

```html
<div {% shard_alpine component %}>
<div {% shard_alpine component tab="home" %}>
```

## shard_child

Render a nested child component from within a component template.

```django
{% shard_child "Counter" initial=5 step=1 %}
```

Uses the parent `component` from context when available.
