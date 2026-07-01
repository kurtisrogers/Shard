# Alpine.js integration

Alpine.js is bundled for client-side interactivity that doesn't need a server round-trip.

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

## No build step

Alpine is included as a static file. You write directives directly in Django templates. No `x-data` compilation or component registration on the client.
