# Quickstart

This walkthrough builds a stateful counter component from scratch.

## 1. Create a component class

```python
# myapp/components.py
from shard import Component, Prop, action

class Counter(Component):
    initial = Prop(int, default=0)
    step = Prop(int, default=1)
    template_name = "components/counter.html"

    def get_initial_state(self):
        return {"count": self.initial}

    @action
    def increment(self, state):
        state["count"] += self.step
        return state

    @action
    def decrement(self, state):
        state["count"] -= self.step
        return state
```

Shard auto-discovers components from `<app>.components` when the app is in `INSTALLED_APPS`.

## 2. Create the template

```html
{# templates/components/counter.html #}
<div {% shard_root component %} class="counter">
  <p>Count: {{ state.count }}</p>
  <button type="button" {% shard_htmx component "increment" %}>+</button>
  <button type="button" {% shard_htmx component "decrement" %}>-</button>
</div>
```

## 3. Add scoped styles

```css
/* templates/components/counter.css */
.counter {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
```

Place `counter.css` beside `counter.html`. Shard discovers it automatically and scopes selectors to `[data-shard-scope="counter"]`.

## 4. Use it in a page

```django
{% load shard %}
{% shard_scripts %}

{% component Counter initial=5 step=2 %}{% endcomponent %}
```

## 5. Run the server

```bash
python manage.py runserver
```

Click the buttons. HTMX posts to Shard's action endpoint, the server runs your `@action` method, persists updated state, and returns a re-rendered HTML fragment.

## What happened?

1. `{% component %}` created a `Counter` instance with props `initial=5` and `step=2`
2. State was initialized via `get_initial_state()` → `{"count": 5}`
3. Props, state, and slots were persisted to cache under a unique instance ID
4. HTMX `hx-post` hit `/shard/action/<id>/increment/`
5. Shard loaded state, called `increment`, saved new state, re-rendered the template

That's the full loop. Everything else in Shard builds on these primitives.
