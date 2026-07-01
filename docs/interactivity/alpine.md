# Alpine.js integration

Alpine.js is bundled for client-side interactivity that doesn't need a server round-trip.

For a full walkthrough with examples, see [Working with HTMX and Alpine](../guides/htmx-and-alpine.md).

## When to use Alpine

| Use Alpine for      | Use HTMX/@action for               |
| ------------------- | ---------------------------------- |
| Toggle visibility   | Persisting data                    |
| Focus management    | Validation with server rules       |
| Animations          | Lists, counters, form state        |
| Client-only filters | Anything that must survive refresh |

## Seeding Alpine state

Override `get_client_state()` on your component:

```python
class Dropdown(Component):
    def get_client_state(self):
        return {"open": False}
```

```html
<div {% shard_alpine component %}>
  <button @click="open = !open">Menu</button>
  <div x-show="open" x-transition>{{ slots.default|safe }}</div>
</div>
```

## shard_alpine tag

```html
<div {% shard_alpine component %}></div>
```

Outputs:

```html
x-data='{"open": false}'
```

Pass extra keys:

```html
<div {% shard_alpine component tab="settings" %}></div>
```

## Combining Alpine and HTMX

Alpine handles immediate UI feedback. HTMX handles persistence:

```html
<div {% shard_alpine component %}>
  <form {% shard_htmx component "save" %} @submit.prevent="$el.requestSubmit()">
    <input
      name="draft"
      @focus="focused = true"
      @blur="focused = false"
    />
    <button type="submit" :disabled="!focused">Save</button>
  </form>
</div>
```

## Listening for Shard events

Action responses trigger HTMX events. Listen with Alpine:

```html
<div {% shard_alpine component %} @todo:added.window="focused = false"></div>
```

Or in `shard.js` / your own scripts:

```javascript
document.body.addEventListener("shard:action-complete", () => {
  // any action completed
});
```

## Loading order

`{% shard_scripts %}` loads:

1. `htmx.min.js` (defer)
2. `alpine.min.js` (defer)
3. `shard.js` (defer)

All scripts use `defer`, so order is preserved and DOM is ready.

## Example: client-only dropdown

Alpine handles open/close with no server round-trip:

```python
class Dropdown(Component):
    template_name = "components/dropdown.html"

    def get_client_state(self) -> dict:
        return {"open": False}
```

```django
{% load shard %}
<div {% shard_root component %} {% shard_alpine component %}>
  <button type="button" @click="open = !open">Menu</button>
  <div x-show="open" x-transition @click.outside="open = false">
    {{ slots.default|safe }}
  </div>
</div>
```

`{% shard_alpine component %}` outputs `x-data='{"open": false}'` from `get_client_state()`.

## Example: TodoList (Alpine + HTMX together)

The example app combines both tools on one root element:

```django
<div {% shard_root component %} {% shard_alpine component %}>
  <form {% shard_htmx component "add_item" %} @submit.prevent="$el.requestSubmit()">
    <input
      name="text"
      {% shard_htmx component "set_draft" trigger="keyup changed delay:300ms" %}
      @focus="focused = true"
      @blur="focused = false"
    />
    <button type="submit">Add</button>
  </form>
</div>
```

| Layer | Responsibility |
| ----- | -------------- |
| Alpine (`focused`) | Immediate focus UI |
| HTMX (`set_draft`) | Debounced sync of draft text to server |
| HTMX (`add_item`) | Persist new item on submit |

Full walkthrough: [Working with HTMX and Alpine](../guides/htmx-and-alpine.md#workflow-combining-alpine-and-htmx). Source: `example/templates/components/todo_list.html`.

## Example: listening for HTMX events

When another component's action fires `@emits("todo:added")`, react in Alpine:

```html
<div {% shard_alpine component %} @todo:added.window="focused = false"></div>
```

The `.window` modifier listens for events HTMX dispatches on `document`.

## Shared and global state

`{% shard_alpine %}` seeds **per-component** `x-data` from `get_client_state()`. Shard does not ship a global Alpine store.

| Need | Use |
| ---- | --- |
| Persisted data | Server `state` + HTMX |
| One component's UI chrome | `get_client_state()` |
| Cross-component signals | HTMX events (`@emits`, `@event.window`) |
| Page layout (sidebar, theme) | Page `x-data` from Django or `Alpine.store()` in your layout script |

Full guidance and examples: [Shared and global client state](../guides/htmx-and-alpine.md#shared-and-global-client-state).

## No build step

Alpine is included as a static file. You write directives directly in Django templates. No `x-data` compilation or component registration on the client.
