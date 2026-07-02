# HTMX integration

Shrd is built around HTMX for server-driven UI updates. HTMX is bundled — no CDN or npm install needed.

For a full walkthrough with examples, see [Working with HTMX and Alpine](../guides/htmx-and-alpine.md).

## Loading HTMX

```django
{% load shard %}
{% shard_scripts %}
```

This loads `htmx.min.js`, `alpine.min.js`, and a small `shard.js` glue file.

## The action loop

```
User click
  → HTMX POST /shard/action/<instance_id>/<action>/
  → Shrd loads state from cache
  → @action method runs
  → State saved
  → Component re-rendered
  → HTML fragment returned
  → HTMX swaps into DOM
```

## shard_htmx tag

Generates common HTMX attributes:

```html
<button {% shard_htmx component "increment" %}>+</button>
```

Outputs:

```html
hx-post="/shard/action/abc123/increment/" hx-target="#shard-abc123"
hx-swap="outerHTML"
```

### Options

```html
<button {% shard_htmx component "search" trigger="keyup changed delay:300ms" swap="innerHTML" %}>
```

| Option    | Default       | Description                    |
| --------- | ------------- | ------------------------------ |
| `swap`    | `outerHTML`   | HTMX swap strategy             |
| `target`  | `#shard-<id>` | Target selector                |
| `trigger` | (none)        | HTMX trigger expression        |
| `include` | (none)        | `hx-include` selector          |
| `**vals`  | (none)        | Extra POST values as `hx-vals` |

## Swap strategies

| Strategy    | Use when                                 |
| ----------- | ---------------------------------------- |
| `outerHTML` | Replacing the entire component (default) |
| `innerHTML` | Updating content inside the root element |
| `beforeend` | Appending to a list                      |

For `innerHTML` swaps, put `{% shard_root component %}` on a wrapper and target a child:

```html
<div {% shard_root component %}>
  <div id="content-{{ shard_id }}">...</div>
</div>
```

```html
<button {% shard_htmx component "refresh" target="#content-..." swap="innerHTML" %}>
```

## Events

Every action response includes an `HX-Trigger` header:

```json
{ "shard:action-complete": true, "counter:changed": true }
```

Listen in Alpine or vanilla JS:

```javascript
document.body.addEventListener("counter:changed", (e) => {
  console.log("Counter updated");
});
```

Declare events on actions with `@emits`:

```python
@emits("counter:changed")
@action
def increment(self, state):
    ...
```

Prefer events over a shared Alpine store when components only need to **react** to each other. See [Shared and global client state](../guides/htmx-and-alpine.md#shared-and-global-client-state).

## Redirects

Return `ActionResult(redirect="/somewhere/")` to trigger `HX-Redirect`.

## CSRF

HTMX includes the CSRF token automatically when using `hx-post` on forms or elements within a page that has `{% csrf_token %}` in a form, or when `hx-headers` is configured. Django's CSRF middleware validates all action requests.

## Debugging

In development, open browser DevTools → Network. Action requests show:

- Request URL with instance ID and action name
- POST body with form fields
- Response HTML fragment
- `HX-Trigger` response header

Use `python manage.py shard_list` to see registered actions per component.

## Example: Counter component

End-to-end HTMX-only component from the example app.

**Python** — state and actions:

```python
class Counter(Component):
    initial = Prop(int, default=0)
    step = Prop(int, default=1)
    template_name = "components/counter.html"

    def get_initial_state(self) -> dict:
        return {"count": self.initial}

    @action
    def increment(self, state: dict) -> dict:
        state["count"] += self.step
        return state
```

**Template** — one line per button:

```django
{% load shard %}
<div {% shard_root component %} class="counter">
  <span>{{ state.count }}</span>
  <button type="button" {% shard_htmx component "increment" %}>+{{ props.step }}</button>
</div>
```

**On click:** HTMX POSTs to `/shard/action/<id>/increment/`, Shrd runs the action, re-renders the component, and swaps `#shard-<id>` with the new HTML.

See `example/templates/components/counter.html` in the repository.

## Example: form POST parameters

Pass input values to action handlers via `name` attributes:

```html
<input name="text" type="text" />
<button {% shard_htmx component "add_item" %}>Add</button>
```

```python
@action
def add_item(self, state, text: str = ""):
    if text.strip():
        state["items"].append(text.strip())
    return state
```

## Example: debounced input

Sync server state on keyup without submitting a form:

```html
<input
  name="draft"
  value="{{ state.draft }}"
  {% shard_htmx component "set_draft" trigger="keyup changed delay:300ms" %}
/>
```

Used in `TodoList` — see [Working with HTMX and Alpine](../guides/htmx-and-alpine.md#workflow-combining-alpine-and-htmx).

## Example: extra POST values

Pass values that are not form fields:

```html
<button {% shard_htmx component "remove_item" index=forloop.counter0 %}>Remove</button>
```

```python
@action
def remove_item(self, state, index: str = "0"):
    state["items"].pop(int(index))
    return state
```
