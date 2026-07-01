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

The demo also includes a [view data](guides/view-data.md) page at http://127.0.0.1:8000/dynamic/ — a layout built from a structured component tree that can be mutated via HTMX actions.

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

Combines server state (`items`, `draft`) with Alpine client state (`focused`) and `ActionResult` events. See [Working with HTMX and Alpine](guides/htmx-and-alpine.md) for a full walkthrough of the template patterns (debounced `set_draft`, form submit, focus tracking).

### Counter

HTMX-only component — buttons call `@action` methods and the whole component re-renders. Documented in [Working with HTMX and Alpine](guides/htmx-and-alpine.md#workflow-building-an-htmx-only-component).

### ViewPage (view data)

`ViewTreeComponent` subclass that stores a layout descriptor in state. Demonstrates adding/removing cards and toggling the footer while preserving child component state.

## Example file map

| File                                  | Purpose               |
| ------------------------------------- | --------------------- |
| `example/components.py`               | All component classes |
| `example/demo_view_data.py`           | Demo view-data trees  |
| `example/templates/home.html`         | Demo page composition |
| `example/templates/dynamic.html`      | View data demo shell  |
| `example/templates/components/*.html` | Component templates   |
| `example/templates/components/*.css`  | Scoped styles         |

## Try modifying

1. Add a new prop to `Button` and use it in the template
2. Create a `Panel` wrapper with a `sidebar` named slot
3. Add `@emits` to `Counter.decrement` and log the event in Alpine
4. Run `python manage.py shard_list` to verify registration
