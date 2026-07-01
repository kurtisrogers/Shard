"""Demo view-data trees for the example application."""

from __future__ import annotations

import copy

from shard import ViewNode, ensure_node_ids

EXAMPLE_ALLOWED_COMPONENTS = frozenset(
    {
        "Alert",
        "Button",
        "Card",
        "Counter",
        "Layout",
        "TodoList",
    }
)

DEMO_VIEW_DATA: ViewNode = {
    "component": "Layout",
    "slots": {
        "header": [
            {
                "component": "Alert",
                "props": {"level": "info", "message": "This page was built from view data."},
            }
        ],
        "default": [
            {
                "component": "Card",
                "props": {"title": "Counter"},
                "children": [
                    {"component": "Counter", "props": {"initial": 3, "step": 2}},
                ],
            },
            {
                "component": "Card",
                "props": {"title": "Todo list"},
                "children": [
                    {"component": "TodoList", "props": {"placeholder": "What needs doing?"}},
                ],
            },
            {
                "component": "Card",
                "props": {"title": "Wrapped actions"},
                "children": [
                    {
                        "component": "Button",
                        "props": {"variant": "primary"},
                        "content": "Primary action",
                    },
                    {
                        "component": "Button",
                        "props": {"variant": "ghost"},
                        "content": "Secondary action",
                    },
                ],
            },
        ],
        "footer": [
            {
                "component": "Alert",
                "props": {
                    "level": "success",
                    "message": "View data layout — mutate via ViewPage actions.",
                },
            }
        ],
    },
}


def initial_demo_view_tree() -> ViewNode:
    """Return the demo tree with stable instance ids."""

    return ensure_node_ids(copy.deepcopy(DEMO_VIEW_DATA))
