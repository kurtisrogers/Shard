from shard import Component, Prop, action


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

    @action
    def increment(self, state: dict) -> dict:
        state["count"] += self.step
        return state

    @action
    def decrement(self, state: dict) -> dict:
        state["count"] -= self.step
        return state


class TodoList(Component):
    placeholder = Prop(str, default="Add a task...")

    template_name = "components/todo_list.html"

    def get_initial_state(self) -> dict:
        return {"items": [], "draft": ""}

    @action
    def add_item(self, state: dict, text: str = "") -> dict:
        value = (text or state.get("draft", "")).strip()
        if value:
            state.setdefault("items", []).append(value)
            state["draft"] = ""
        return state

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
