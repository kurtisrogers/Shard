# Working with HTMX and Alpine

Shrd uses **HTMX** for server-driven updates and **Alpine.js** for client-side UI that does not need a round-trip. Both are bundled as static files — no npm, no build step.

This guide walks through how developers actually build interactive components: the workflow, when to reach for each tool, and full examples from the repository.

## Mental model

```
┌─────────────────────────────────────────────────────────────┐
│  Page template                                              │
│  {% shard_scripts alpine=True %}   ← load once per page     │
│  {% component Counter %}{% endcomponent %}                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Component template                                         │
│  {% shard_root component %}        ← HTMX swap target       │
│  {% shard_htmx component "increment" %}  ← POST to server   │
│  {% shard_alpine component %}      ← optional client state  │
└─────────────────────────────────────────────────────────────┘
                              │
              User click ─────┴─────► POST /shard/action/<id>/<action>/
                                            │
                                            ▼
                              @action method updates state
                                            │
                                            ▼
                              Component re-rendered → HTML fragment
                                            │
                                            ▼
                              HTMX swaps fragment into DOM
```

**HTMX** owns persistence: counters, lists, form saves, validation. The server is the source of truth.

**Alpine** owns ephemeral UI: open/closed panels, focus rings, transitions, disabling a button while typing. It resets on full page reload unless you mirror values in server state.

See also: [Actions](../interactivity/actions.md), [HTMX](../interactivity/htmx.md), [Alpine](../interactivity/alpine.md), [Events](../interactivity/events.md).

## Page setup

Load scripts once in your page layout. Pass `alpine=True` when any component on the page uses `{% shard_alpine %}`:

```django
{% load shard %}
{% shard_scripts alpine=True %}
```

The example app does this in `example/templates/home.html`. Without Alpine on the page, `x-data` directives are inert.

| Script          | Purpose                                            |
| --------------- | -------------------------------------------------- |
| `htmx.min.js`   | POST actions, swap HTML fragments                  |
| `alpine.min.js` | `x-data`, `x-show`, `@click`, etc.                 |
| `shard.js`      | Adds `shard=1` to HTMX requests (framework marker) |

## Workflow: building an HTMX-only component

Use HTMX alone when every interaction should update server state and re-render the component.

### 1. Define state and actions in Python

```python
# example/components.py
from shard import Component, Prop, action, computed, emits

class Counter(Component):
    initial = Prop(int, default=0)
    step = Prop(int, default=1)
    template_name = "components/counter.html"

    def get_initial_state(self) -> dict:
        return {"count": self.initial}

    @computed
    def label(self) -> str:
        return f"Current count is {self.state['count']}"

    @emits("counter:changed")
    @action
    def increment(self, state: dict) -> dict:
        state["count"] += self.step
        return state

    @emits("counter:changed")
    @action
    def decrement(self, state: dict) -> dict:
        state["count"] -= self.step
        return state
```

### 2. Wire buttons in the template

```django
{# example/templates/components/counter.html #}
{% load shard %}
<div {% shard_root component %} class="counter">
  <p class="counter__value">
    <strong>Count:</strong>
    <span>{{ state.count }}</span>
  </p>
  <p class="counter__label"><small>{{ computed.label }}</small></p>
  <div class="counter__actions">
    <button type="button" class="counter__btn" {% shard_htmx component "increment" %}>
      +{{ props.step }}
    </button>
    <button type="button" class="counter__btn" {% shard_htmx component "decrement" %}>
      -{{ props.step }}
    </button>
  </div>
</div>
```

### 3. What happens on click

`{% shard_htmx component "increment" %}` expands to:

```html
hx-post="/shard/action/<instance_id
  >/increment/" hx-target="#shard-<instance_id
    >" hx-swap="outerHTML"</instance_id
  ></instance_id
>
```

HTMX POSTs to Shrd, the `increment` action runs, state is saved, the component re-renders, and HTMX replaces the entire `#shard-<id>` element with the new HTML. The count in the response always matches server state.

### 4. Mount on a page

```django
{% component Card title="Counter" %}
  {% component Counter initial=3 step=2 %}{% endcomponent %}
{% endcomponent %}
```

Or from a view with `mount(Counter, props={"initial": 3})`.

### 5. Listen for events (optional)

`@emits("counter:changed")` adds that event to the `HX-Trigger` response header. Other components or page scripts can react:

```javascript
document.body.addEventListener("counter:changed", () => {
  console.log("Counter updated");
});
```

## Workflow: combining Alpine and HTMX

Use both when you need **immediate client feedback** and **server persistence** in the same component. The example `TodoList` is the canonical pattern.

### 1. Split server state and client state

```python
class TodoList(Component):
    placeholder = Prop(str, default="Add a task...")
    template_name = "components/todo_list.html"

    def get_initial_state(self) -> dict:
        return {"items": [], "draft": ""}  # persisted on server

    def get_client_state(self) -> dict:
        return {"focused": False}  # Alpine only; resets on full reload

    @action
    def add_item(self, state: dict, text: str = "") -> ActionResult:
        value = (text or state.get("draft", "")).strip()
        if value:
            state.setdefault("items", []).append(value)
            state["draft"] = ""
            return ActionResult.with_events(state, **{"todo:added": {"item": value}})
        return ActionResult(state=state)

    @action
    def set_draft(self, state: dict, draft: str = "") -> dict:
        state["draft"] = draft
        return state

    @action
    def remove_item(self, state: dict, index: str = "0") -> dict:
        ...
```

| Data             | Where                         | Updated by                |
| ---------------- | ----------------------------- | ------------------------- |
| `items`, `draft` | `state` (server)              | `@action` methods         |
| `focused`        | `get_client_state()` (client) | Alpine `@focus` / `@blur` |

### 2. Template: Alpine on the root, HTMX on controls

```django
{# example/templates/components/todo_list.html #}
{% load shard %}
<div {% shard_root component %} class="todo" {% shard_alpine component %}>
  <form
    class="todo__form"
    {% shard_htmx component "add_item" %}
    @submit.prevent="$el.requestSubmit()"
  >
    <input
      class="todo__input"
      type="text"
      name="text"
      placeholder="{{ props.placeholder }}"
      value="{{ state.draft }}"
      {% shard_htmx component "set_draft" trigger="keyup changed delay:300ms" %}
      @focus="focused = true"
      @blur="focused = false"
    />
    <button class="todo__submit" type="submit">Add</button>
  </form>

  {% if state.items %}
    <ul class="todo__items">
      {% for item in state.items %}
        <li class="todo__item">
          <span>{{ item }}</span>
          <button
            type="button"
            class="todo__remove"
            {% shard_htmx component "remove_item" index=forloop.counter0 %}
          >
            Remove
          </button>
        </li>
      {% endfor %}
    </ul>
  {% else %}
    <p class="todo__empty"><em>No tasks yet.</em></p>
  {% endif %}
</div>
```

Key techniques in this template:

| Technique                                                           | Why                                                              |
| ------------------------------------------------------------------- | ---------------------------------------------------------------- |
| `{% shard_alpine component %}` on root                              | Seeds `x-data='{"focused": false}'` from `get_client_state()`    |
| `{% shard_htmx component "add_item" %}` on `<form>`                 | Submit POSTs `text` field to `add_item`                          |
| `@submit.prevent="$el.requestSubmit()"`                             | Alpine prevents full navigation; HTMX handles the POST           |
| `{% shard_htmx ... trigger="keyup changed delay:300ms" %}` on input | Debounced draft sync to server without submitting                |
| `name="text"` on input                                              | Becomes `text=` keyword arg in `add_item(self, state, text=...)` |
| `index=forloop.counter0` on remove button                           | Passed as `index=` to `remove_item` via `hx-vals`                |

### 3. Debounced server sync

The draft input fires `set_draft` on keyup (300 ms debounce). Server state stays in sync if the user navigates away mid-edit, while Alpine handles focus styling without a round-trip:

```html
<input
  {% shard_htmx component "set_draft" trigger="keyup changed delay:300ms" %}
  @focus="focused = true"
  @blur="focused = false"
/>
```

You could also use `:class="{ 'is-focused': focused }"` for visual feedback driven by Alpine.

## When to use HTMX vs Alpine

| Task                      | Tool             | Example                           |
| ------------------------- | ---------------- | --------------------------------- |
| Increment a counter       | HTMX             | `Counter.increment`               |
| Persist a todo list       | HTMX             | `TodoList.add_item`               |
| Sync draft text to server | HTMX (debounced) | `TodoList.set_draft`              |
| Track input focus         | Alpine           | `focused` in `get_client_state()` |
| Toggle a dropdown open    | Alpine           | `open = !open`                    |
| Animate panel enter/leave | Alpine           | `x-show` + `x-transition`         |
| Save form to database     | HTMX             | `@action` + `ActionResult`        |
| Navigate after save       | HTMX             | `ActionResult(redirect="/done/")` |

**Rule of thumb:** if it must survive a component re-render or page refresh, put it in server `state`. If it is purely visual and ephemeral, use Alpine.

## Shared and global client state

Shrd seeds Alpine state **per component** via `get_client_state()` and `{% shard_alpine %}`. There is no built-in global Alpine store — that is intentional. The server remains the source of truth; Alpine handles local UI chrome.

### What Shrd provides

| Need                                | Mechanism                                   |
| ----------------------------------- | ------------------------------------------- |
| Persisted data                      | Server `state` + `@action`                  |
| Component UI (focus, open, animate) | `get_client_state()` on that component      |
| "A did something, B should react"   | `@emits` / `ActionResult` + `@event.window` |
| Layout spanning multiple components | See patterns below                          |

### Why not a framework global Alpine store?

A Shrd-managed global client store would introduce a second state graph that:

- Does not sync automatically with server `state` after HTMX re-renders
- Survives `outerHTML` swaps differently from per-component `x-data` (sometimes useful, often a source of stale UI)
- Encourages SPA-style patterns Shrd deliberately avoids

For shared client UI, use one of the patterns below in **your app code**. Shrd documents them; it does not need to own them.

### Decision guide

| Need                                       | Recommended approach                                |
| ------------------------------------------ | --------------------------------------------------- |
| Counter, list items, form values           | Server `state` + HTMX                               |
| Focus, hover, open/closed on one component | `get_client_state()` on that component              |
| Component A notifies component B           | HTMX events (`@emits`, `@event.window`)             |
| Sidebar/theme across the whole page        | Page-level `x-data` or `Alpine.store()` (app-owned) |
| User preference that survives refresh      | Django session or database, not Alpine alone        |

### Pattern 1: HTMX events (preferred for coordination)

When one component should **react** to another's action — not share a mutable store — use events:

```python
@emits("todo:added")
@action
def add_item(self, state, text: str = ""):
    ...
```

```html
<div {% shard_alpine component %} @todo:added.window="focused = false"></div>
```

See [Events](../interactivity/events.md).

### Pattern 2: Lift client state to a parent

If two children need the same ephemeral UI, put Alpine on a **parent** that is not the HTMX swap target:

```django
{# base.html — parent survives child HTMX swaps #}
<body x-data='{"sidebarOpen": false}'>
  <aside x-show="sidebarOpen">...</aside>
  <main>
    {% component Counter %}{% endcomponent %}
  </main>
</body>
```

Child components re-render via HTMX; layout chrome on `<body>` stays intact.

### Pattern 3: Page-level `x-data` from Django

Seed layout UI once from a view or context processor:

```python
# myapp/context_processors.py
import json

def alpine_layout(request):
    return {
        "alpine_page_state": json.dumps({
            "sidebarOpen": False,
            "theme": request.session.get("theme", "light"),
        }),
    }
```

```django
{# templates/base.html #}
<body x-data='{{ alpine_page_state|safe }}'>
  {% shard_scripts alpine=True %}
  <button @click="sidebarOpen = !sidebarOpen">Menu</button>
  ...
</body>
```

This is standard Django → template → Alpine. Shrd does not wrap it because your app owns what belongs at page scope.

### Pattern 4: `Alpine.store()` for app-wide reactivity

When distant components must read/write the same client value without server round-trips, register a store in your own script:

```django
{% shard_scripts alpine=True %}
<script>
  document.addEventListener("alpine:init", () => {
    Alpine.store("ui", {
      sidebarOpen: false,
      toggleSidebar() {
        this.sidebarOpen = !this.sidebarOpen;
      },
    });
  });
</script>
```

```html
<button @click="$store.ui.toggleSidebar()">Menu</button>
<aside x-show="$store.ui.sidebarOpen">...</aside>
```

Keep stores **small and UI-only**. Do not mirror server `state` in a global Alpine store — it will drift after HTMX swaps.

### What to avoid

- Putting persisted business data (lists, counts, form values) in `Alpine.store()`
- Expecting global Alpine state to survive HTMX `outerHTML` swaps on the same element that owns it
- Using a global store when HTMX events or server `state` would be simpler

## Common patterns

### POST form fields to an action

Any `name` attribute in the request becomes a keyword argument:

```html
<input name="email" type="email" />
<button {% shard_htmx component "subscribe" %}>Subscribe</button>
```

```python
@action
def subscribe(self, state, email: str = ""):
    state["email"] = email.strip()
    return state
```

### Pass extra values without a form field

```html
<button {% shard_htmx component "remove_item" index=forloop.counter0 %}>Remove</button>
```

Renders `hx-vals='{"index": 0}'` alongside the POST.

### Manual HTMX attributes

`shard_htmx` is sugar. Equivalent manual markup:

```html
<button
  hx-post="{{ shard_actions.increment }}"
  hx-target="#shard-{{ shard_id }}"
  hx-swap="outerHTML"
>
  +
</button>
```

Use manual attributes when you need custom targets or swap strategies not covered by the tag.

### Partial updates (`innerHTML` swap)

Default `outerHTML` replaces the whole component including scoped styles on first load. For large components, target an inner region:

```html
<div {% shard_root component %}>
  <header>...</header>
  <div id="results-{{ shard_id }}">{{ state.results_html|safe }}</div>
</div>

<button {% shard_htmx component "search" target="#results-{{ shard_id }}" swap="innerHTML" %}>
  Search
</button>
```

### Alpine dropdown (client-only)

No HTMX needed when nothing is persisted:

```python
class Dropdown(Component):
    template_name = "components/dropdown.html"

    def get_client_state(self) -> dict:
        return {"open": False}
```

```django
{% load shard %}
<div {% shard_root component %} {% shard_alpine component %} class="dropdown">
  <button type="button" @click="open = !open" :aria-expanded="open">
    Menu
  </button>
  <div x-show="open" x-transition @click.outside="open = false">
    {{ slots.default|safe }}
  </div>
</div>
```

### React to another component's event in Alpine

```html
<div {% shard_alpine component %} @todo:added.window="focused = false"></div>
```

`@emits` / `ActionResult` events are fired on `document` via HTMX's `HX-Trigger` header.

## Debugging

1. **Network tab** — action requests go to `/shard/action/<instance_id>/<action_name>/`. Check POST body, response HTML, and `HX-Trigger` header.
2. **`python manage.py shard_list`** — lists registered components and their actions.
3. **Missing swap** — ensure `{% shard_root component %}` is on the element HTMX targets (`#shard-<id>` by default).
4. **Alpine not working** — confirm `{% shard_scripts alpine=True %}` is on the page.
5. **CSRF errors** — include `{% csrf_token %}` somewhere on the page (Django convention).
6. **State 404** — instance expired or cache cleared; remount the component.

## Try the examples

```bash
pip install -e ".[dev]"
cd example
python manage.py runserver
```

- http://127.0.0.1:8000/ — `Counter` (HTMX) and `TodoList` (Alpine + HTMX)
- http://127.0.0.1:8000/dynamic/ — view-data layout with HTMX toolbar actions

Source files:

| Component | Python                  | Template                                      |
| --------- | ----------------------- | --------------------------------------------- |
| Counter   | `example/components.py` | `example/templates/components/counter.html`   |
| TodoList  | `example/components.py` | `example/templates/components/todo_list.html` |
