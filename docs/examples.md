# Examples

The repository includes a runnable example app in `example/`.

## Running the demo

```bash
pip install -e ".[dev]"
cd example
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Components demonstrated

### Layout

Multi-slot page shell with `header`, default, and `footer` slots.

```django
{% component Layout %}
  {% slot header %}<h1>Shard</h1>{% endslot %}
  ...
  {% slot footer %}<small>Footer</small>{% endslot %}
{% endcomponent %}
```

### Card (wrapper)

Accepts arbitrary slot content with optional `title` prop and scoped `.card` styles.

### Button (wrapper)

Wraps label text with `variant` prop (`default`, `primary`, `ghost`).

### Alert

Demonstrates `@computed` for dynamic CSS classes.

### Counter

Stateful component with `@action`, `@computed`, `@emits`, and `shard_htmx`.

### TodoList

Combines server state (`items`, `draft`) with Alpine client state (`focused`) and `ActionResult` events.

## Example file map

| File | Purpose |
|------|---------|
| `example/components.py` | All component classes |
| `example/templates/home.html` | Demo page composition |
| `example/templates/components/*.html` | Component templates |
| `example/templates/components/*.css` | Scoped styles |

## Try modifying

1. Add a new prop to `Button` and use it in the template
2. Create a `Panel` wrapper with a `sidebar` named slot
3. Add `@emits` to `Counter.decrement` and log the event in Alpine
4. Run `python manage.py shard_list` to verify registration
