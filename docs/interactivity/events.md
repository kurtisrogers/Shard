# Events

Shard supports HTMX custom events for decoupled communication between components and page-level scripts.

## Declaring events

Use `@emits` above `@action`:

```python
from shard import action, emits

@emits("counter:changed")
@action
def increment(self, state):
    state["count"] += 1
    return state
```

After the action completes, HTMX fires `counter:changed` on the document.

## ActionResult events

For dynamic event payloads:

```python
from shard import ActionResult, action

@action
def add_item(self, state, text: str = ""):
    value = text.strip()
    if value:
        state["items"].append(value)
        return ActionResult.with_events(
            state,
            **{"todo:added": {"item": value}}
        )
    return ActionResult(state=state)
```

## Built-in event

Every action also triggers `shard:action-complete`:

```javascript
document.addEventListener("shard:action-complete", () => {
  console.log("A component action finished");
});
```

## Listening in Alpine

```html
<div @counter:changed.window="onCounterChange()"></div>
```

## Listening in vanilla JS

```javascript
document.body.addEventListener("todo:added", (event) => {
  const detail = event.detail;
  // detail contains the payload from ActionResult
});
```

## Redirects

```python
return ActionResult(state=state, redirect="/done/")
```

Sets the `HX-Redirect` response header. HTMX navigates the browser.

## Event naming conventions

Use namespaced events to avoid collisions:

- `counter:changed`
- `todo:added`
- `form:saved`

Shard does not enforce a schema — choose conventions that fit your app.
