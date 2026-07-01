from example.demo_view_data import EXAMPLE_ALLOWED_COMPONENTS, initial_demo_view_tree
from shard import (
    ActionResult,
    Component,
    Prop,
    ViewTreeComponent,
    action,
    computed,
    emits,
    ensure_node_ids,
    get_slot_nodes,
    set_slot_nodes,
)


class Layout(Component):
    """Page shell with header, main, and footer slots."""

    template_name = "components/layout.html"


class Card(Component):
    title = Prop(str, default="")

    template_name = "components/card.html"


class Button(Component):
    variant = Prop(str, default="default")
    button_type = Prop(str, default="button")

    template_name = "components/button.html"


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


class Alert(Component):
    message = Prop(str, default="")
    level = Prop(str, default="info")

    template_name = "components/alert.html"

    @computed
    def css_class(self) -> str:
        return f"alert alert--{self.level}"


class TodoList(Component):
    placeholder = Prop(str, default="Add a task...")

    template_name = "components/todo_list.html"

    def get_initial_state(self) -> dict:
        return {"items": [], "draft": ""}

    def get_client_state(self) -> dict:
        return {"focused": False}

    @action
    def add_item(self, state: dict, text: str = "") -> ActionResult:
        value = (text or state.get("draft", "")).strip()
        if value:
            state.setdefault("items", []).append(value)
            state["draft"] = ""
            return ActionResult.with_events(state, **{"todo:added": {"item": value}})
        return ActionResult(state=state)

    @action
    def remove_item(self, state: dict, index: str = "0") -> dict:
        items = state.get("items", [])
        try:
            items.pop(int(index))
        except (ValueError, IndexError):
            pass
        state["items"] = items
        return state

    @action
    def set_draft(self, state: dict, draft: str = "") -> dict:
        state["draft"] = draft
        return state


class ViewPage(ViewTreeComponent):
    """Demo page with a mutable layout driven by view data in server state."""

    allowed_view_components = EXAMPLE_ALLOWED_COMPONENTS
    template_name = "components/view_page.html"

    def get_initial_state(self) -> dict:
        return {"tree": initial_demo_view_tree(), "footer_visible": True}

    @computed
    def card_count(self) -> int:
        return len(get_slot_nodes(self.state["tree"], "default"))

    @action
    def add_card(self, state: dict) -> dict:
        tree = state["tree"]
        cards = get_slot_nodes(tree, "default")
        next_index = len(cards) + 1
        cards.append(
            ensure_node_ids(
                {
                    "component": "Card",
                    "props": {"title": f"Dynamic card {next_index}"},
                    "children": [
                        {"component": "Counter", "props": {"initial": 0, "step": 1}},
                    ],
                }
            )
        )
        self.commit_view_tree(state, set_slot_nodes(tree, "default", cards))
        return state

    @action
    def remove_last_card(self, state: dict) -> dict:
        tree = state["tree"]
        cards = get_slot_nodes(tree, "default")
        if cards:
            self.commit_view_tree(state, set_slot_nodes(tree, "default", cards[:-1]))
        return state

    @action
    def toggle_footer(self, state: dict) -> dict:
        tree = state["tree"]
        footer_visible = not state.get("footer_visible", True)
        if footer_visible:
            footer = [
                ensure_node_ids(
                    {
                        "component": "Alert",
                        "props": {
                            "level": "success",
                            "message": "Footer restored from view-data state.",
                        },
                    }
                )
            ]
        else:
            footer = []
        self.commit_view_tree(state, set_slot_nodes(tree, "footer", footer))
        state["footer_visible"] = footer_visible
        return state
