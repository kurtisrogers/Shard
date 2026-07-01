# Shard

**Shard** is a Django-native component framework. It gives you a familiar model for building UI — props, state, slots, scoped styles — without leaving the Django ecosystem or adding a JavaScript build step.

Shard is a **framework**, not a widget library. It does not ship pre-built components. Instead, it provides conventions and primitives so you can author your own components the way you would in React or Vue, but lighter and less opinionated.

## What you get

| Feature           | Description                                                   |
| ----------------- | ------------------------------------------------------------- |
| **Props**         | Typed inputs declared on Python component classes             |
| **State**         | Server-owned data updated via `@action` methods               |
| **Slots**         | Wrap and compose markup like `children` / Vue slots           |
| **Scoped styles** | Co-located `.css` files, automatically prefixed per component |
| **HTMX**          | Partial re-renders after server actions                       |
| **Alpine.js**     | Optional client-side behavior inside templates                |

## Quick example

```python
# myapp/components.py
from shard import Component, Prop

class Card(Component):
    title = Prop(str, default="")
    template_name = "components/card.html"
```

```django
{# page template #}
{% load shard %}
{% shard_scripts %}

{% component Card title="Profile" %}
  <p>Anything here is passed through the default slot.</p>
{% endcomponent %}
```

## Why Shard?

Django templates are great for rendering pages, but they lack a first-class component model. Most teams reach for React or Vue SPAs, which introduces a separate build pipeline, API boundaries, and operational complexity.

Shard keeps you in Django:

- Components are Python classes in your apps
- Templates are standard Django templates
- Styles are plain CSS files beside your templates
- Interactivity uses bundled HTMX and Alpine.js
- No webpack, no Vite, no separate frontend repo

## Next steps

- [Installation](getting-started/installation.md)
- [Quickstart](getting-started/quickstart.md)
- [Core concepts](concepts/philosophy.md)
- [Testing your project](guides/testing.md)
- [Examples](examples.md)
