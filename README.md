# Shard

A Django-native component framework for building UI with **props**, **server state**, **slots**, and **scoped styles** — using only the Django ecosystem plus bundled HTMX and Alpine.js.

Shard is a framework, not a drop-in library. Your Django project adopts its conventions: components live in your apps, templates sit beside scoped CSS, and HTMX carries server actions.

## Philosophy

Shard does not ship a widget catalog. It gives you a small, familiar model — closer to React/Vue than to Django templates alone — without a build step or SPA complexity:

- **Props** — typed inputs declared on a Python class
- **State** — server-owned data updated via `@action` methods
- **Slots** — wrap and compose markup like `children` / default slots
- **Scoped styles** — co-located `.css` files, automatically prefixed to the component
- **HTMX** — partial re-renders after actions
- **Alpine.js** — optional client-side behavior inside templates

## Quick start

```python
# myapp/components.py
from shard import Component, Prop, action

class Card(Component):
    title = Prop(str, default="")

    template_name = "components/card.html"
```

```html
{# templates/components/card.html #}
<article data-shard-scope="{{ shard_scope }}" id="shard-{{ shard_id }}" class="card">
  {% if props.title %}<h2 class="card__title">{{ props.title }}</h2>{% endif %}
  <div class="card__body">{{ slots.default|safe }}</div>
</article>
```

```css
/* templates/components/card.css — auto-discovered & scoped */
.card {
  border: 1px solid #ccc;
  border-radius: 0.75rem;
  padding: 1rem;
}
```

```django
{% load shard %}
{% shard_scripts %}

{% component Card title="Profile" %}
  <p>Anything here is passed through the default slot.</p>
{% endcomponent %}
```

### Named slots

```django
{% component Layout %}
  {% slot header %}<h1>Dashboard</h1>{% endslot %}
  <p>Main content uses the default slot.</p>
  {% slot footer %}<small>© You</small>{% endslot %}
{% endcomponent %}
```

Access in templates with `{{ slots.header }}`, `{{ slots.default }}`, etc.

## Stateful components

```python
class Counter(Component):
    step = Prop(int, default=1)
    template_name = "components/counter.html"

    def get_initial_state(self):
        return {"count": 0}

    @action
    def increment(self, state):
        state["count"] += self.step
        return state
```

```html
<button
  hx-post="{{ shard_actions.increment }}"
  hx-target="#shard-{{ shard_id }}"
  hx-swap="outerHTML"
>
  {{ state.count }}
</button>
```

## Project setup

```python
INSTALLED_APPS = [
    # ...
    "shard",
    "myapp",
]

urlpatterns = [
    path("shard/", include("shard.urls")),
]
```

Place components in `myapp/components.py`. Shard auto-discovers them at startup.

### Settings

| Setting | Default | Purpose |
|---------|---------|---------|
| `SHARD_STATE_TIMEOUT` | `86400` | Seconds to keep component state in cache |
| `SHARD_AUTODISCOVER` | `True` | Import `<app>.components` automatically |

## Template context

Every component template receives:

| Variable | Description |
|----------|-------------|
| `props` | Resolved prop values |
| `state` | Current server state |
| `slots` | Dict of rendered slot HTML |
| `shard_id` | Unique instance id (for HTMX targets) |
| `shard_scope` | Stable scope key for styling |
| `shard_actions` | Map of action name → URL |

## Scoped styling

1. Add `data-shard-scope="{{ shard_scope }}"` on your root element (recommended).
2. Place a `.css` file next to your `.html` template (`card.html` → `card.css`).
3. Write normal CSS class names — Shard prefixes selectors with `[data-shard-scope="card"]` at render time.

Disable per component with `scoped_styles = False`, or supply inline CSS via `styles = "..."`.

## Example app

```bash
pip install -e ".[dev]"
cd example
python manage.py migrate
python manage.py runserver
```

## License

MIT
