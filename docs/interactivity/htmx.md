# HTMX integration

Shard is built around HTMX for server-driven UI updates. HTMX is bundled — no CDN or npm install needed.

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
  → Shard loads state from cache
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
hx-post="/shard/action/abc123/increment/"
hx-target="#shard-abc123"
hx-swap="outerHTML"
```

### Options

```html
<button {% shard_htmx component "search" trigger="keyup changed delay:300ms" swap="innerHTML" %}>
```

| Option | Default | Description |
|--------|---------|-------------|
| `swap` | `outerHTML` | HTMX swap strategy |
| `target` | `#shard-<id>` | Target selector |
| `trigger` | (none) | HTMX trigger expression |
| `include` | (none) | `hx-include` selector |
| `**vals` | (none) | Extra POST values as `hx-vals` |

## Swap strategies

| Strategy | Use when |
|----------|----------|
| `outerHTML` | Replacing the entire component (default) |
| `innerHTML` | Updating content inside the root element |
| `beforeend` | Appending to a list |

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
{"shard:action-complete": true, "counter:changed": true}
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
