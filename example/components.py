from shard import ActionResult, Component, Prop, action, computed, emits


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
