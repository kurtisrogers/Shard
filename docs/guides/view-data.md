# View data

Build and mutate page layouts from structured data instead of hand-authored templates. View data describes a tree of registered Shard components; the framework walks that tree, mounts each node, and preserves child state across layout changes.

Use view data when:

- Layout structure comes from your database, CMS, or API
- Users or admins can add, remove, or reorder UI regions at runtime
- You want one declarative format for both initial render and HTMX re-renders

Use templates when layout is fixed and page-specific — view data adds schema and state-management overhead you may not need.

## View node shape

Each node in the tree is a mapping:

```python
{
    "id": "optional-stable-instance-id",  # assigned automatically when missing
    "component": "Card",                  # registered component name
    "props": {"title": "Counter"},        # passed to the component
    "children": [ ... ],                  # rendered into the default slot
    "slots": {                            # named slots (for layouts)
        "header": [ ... ],
        "default": [ ... ],
    },
    "content": "Optional default-slot text",
}
```

- **`component`** — required; must be in your whitelist (see [Security](#security))
- **`children`** — shorthand for default-slot child nodes
- **`slots`** — named slot content as lists of child nodes
- **`content`** — plain text/HTML for the default slot (useful for `Button` labels)
- **`id`** — stable instance id; required for [mutable layouts](#mutable-layouts-via-actions)

## One-shot render

Render a tree once from a Django view:

```python
from shard import render_view_data

VIEW = {
    "component": "Layout",
    "slots": {
        "default": [
            {
                "component": "Card",
                "props": {"title": "Hello"},
                "children": [{"component": "Counter", "props": {"initial": 0}}],
            }
        ],
    },
}

def dashboard(request):
    html = render_view_data(
        VIEW,
        request=request,
        allowed_components=frozenset({"Layout", "Card", "Counter"}),
    )
    return render(request, "page.html", {"content": html})
```

```django
{# page.html #}
{{ content|safe }}
```

For one-shot renders you can omit stable ids and pass `stable=False` (the default). Each mount gets a fresh instance id.

## Mutable layouts via actions

To change layout on HTMX actions, store the descriptor in component **state** and re-render on each request. Subclass `ViewTreeComponent`:

```python
from shard import ViewTreeComponent, action, ensure_node_ids, get_slot_nodes, set_slot_nodes

class Dashboard(ViewTreeComponent):
    allowed_view_components = frozenset({"Layout", "Card", "Counter"})
    template_name = "components/dashboard.html"

    def get_initial_state(self):
        return {
            "tree": ensure_node_ids({
                "component": "Layout",
                "slots": {
                    "default": [
                        {
                            "component": "Card",
                            "props": {"title": "Counter"},
                            "children": [
                                {"component": "Counter", "props": {"initial": 0}},
                            ],
                        }
                    ],
                },
            }),
        }

    @action
    def add_panel(self, state):
        tree = state["tree"]
        panels = get_slot_nodes(tree, "default")
        panels.append(ensure_node_ids({
            "component": "Card",
            "props": {"title": f"Panel {len(panels) + 1}"},
            "children": [{"component": "Counter", "props": {"initial": 0}}],
        }))
        self.commit_view_tree(state, set_slot_nodes(tree, "default", panels))
        return state
```

```django
{# components/dashboard.html #}
{% load shard %}
<div {% shard_root component %}>
  <button type="button" {% shard_htmx component "add_panel" %}>Add panel</button>
  {{ content_html|safe }}
</div>
```

`ViewTreeComponent.render()`:

1. Assigns ids to any new nodes (`ensure_node_ids`)
2. Re-walks the tree with `stable=True` so existing child state is loaded from cache
3. Persists the tree (with ids) back to state

### Mutating the tree in actions

Always commit structural changes through `commit_view_tree()` (or `self.commit_view_tree()` on `ViewTreeComponent`):

```python
self.commit_view_tree(state, new_tree)
```

This replaces the tree in state and **deletes cache entries** for removed node ids. Without pruning, removed components leave orphaned state in cache.

### Preserving child state

When the parent re-renders after a layout change, children must keep the same `id` or their state resets. `ensure_node_ids()` assigns ids on first render; subsequent mutations should preserve ids on unchanged nodes.

Flow:

1. User increments a `Counter` (child state `count: 5`)
2. User triggers `add_panel` on the parent
3. Parent re-renders the tree; the `Counter` node still has the same `id`
4. Stable mount loads `count: 5` from cache

The example app demonstrates this at `/dynamic/`.

## Tree helpers

```python
from shard import (
    commit_view_tree,
    ensure_node_ids,
    get_slot_nodes,
    set_slot_nodes,
)
from shard.view_data import collect_node_ids, prune_orphaned_nodes
```

| Function | Purpose |
| -------- | ------- |
| `ensure_node_ids(tree)` | Assign ids to nodes missing them (returns a copy) |
| `get_slot_nodes(tree, "default")` | Read slot child nodes from the tree root |
| `set_slot_nodes(tree, "default", nodes)` | Return a copy with a slot replaced |
| `commit_view_tree(state, "tree", tree)` | Replace tree in state and prune removed ids |
| `collect_node_ids(tree)` | All instance ids in a tree |
| `prune_orphaned_nodes(ids)` | Delete cache entries for removed ids |

## Security

View data can instantiate any whitelisted component with arbitrary props. **Always use an explicit whitelist** — never pass user-controlled component names without validation.

Two ways to configure the whitelist:

```python
# Per render call
render_view_data(tree, allowed_components=frozenset({"Card", "Counter"}))

# On a ViewTreeComponent subclass
class Dashboard(ViewTreeComponent):
    allowed_view_components = frozenset({"Card", "Counter"})
```

Or globally in settings:

```python
SHARD_VIEW_DATA_ALLOWED_COMPONENTS = [
    "Layout",
    "Card",
    "Counter",
]
```

If neither a per-call/class whitelist nor the setting is configured, `render_view_data()` raises `ViewDataError`.

Slot content and `content` fields are rendered with `|safe` in component templates — do not put untrusted HTML in view data without sanitizing.

## Settings

See [SHARD_VIEW_DATA_ALLOWED_COMPONENTS](../reference/settings.md#shard_view_data_allowed_components).

## Limitations

| Topic | Behavior |
| ----- | -------- |
| Parent/child state | Parent actions mutate the tree; child actions mutate their own state. A parent cannot directly change child state. |
| Scoped CSS | Dynamically added component types on the first HTMX partial may miss scoped styles unless those types were rendered in the initial page load. |
| Cache entries | Each mounted node has its own cache key. Use Redis (not LocMem) when trees are large. |
| Prop types | View data props are plain JSON-serializable values. Nested object prop types are not validated by `Prop`. |

## Example

The repository includes a full demo:

```bash
cd example && python manage.py runserver
# http://127.0.0.1:8000/dynamic/
```

See `example/demo_view_data.py`, `example/components.py` (`ViewPage`), and `tests/test_view_data_integration.py`.
