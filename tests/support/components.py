"""Shared test components and helpers."""

from __future__ import annotations

from shard import ActionResult, Component, Prop, action, computed, emits


class Minimal(Component):
    label = Prop(str, default="hello")
    template_name = "minimal.html"


class Stateful(Component):
    count = Prop(int, default=0)
    template_name = "stateful.html"

    def get_initial_state(self) -> dict:
        return {"value": self.count}

    @action
    def bump(self, state: dict) -> dict:
        state["value"] += 1
        return state


class WithComputed(Component):
    base = Prop(int, default=2)
    template_name = "with_computed.html"

    def get_initial_state(self) -> dict:
        return {"n": self.base}

    @computed
    def doubled(self) -> int:
        return self.state["n"] * 2


class WithHooks(Component):
    template_name = "minimal.html"

    def get_initial_state(self) -> dict:
        return {"log": []}

    def before_action(self, action_name: str, payload: dict) -> None:
        self.state["log"].append(f"before:{action_name}")

    def after_action(self, action_name: str, state: dict) -> None:
        state["log"].append(f"after:{action_name}")

    @action
    def ping(self, state: dict) -> dict:
        state["log"].append("ping")
        return state


class WithEvents(Component):
    template_name = "minimal.html"

    def get_initial_state(self) -> dict:
        return {"n": 0}

    @emits("test:tick")
    @action
    def tick(self, state: dict) -> dict:
        state["n"] += 1
        return state

    @action
    def save(self, state: dict) -> ActionResult:
        return ActionResult.with_events(state, **{"saved": {"ok": True}})


class WithClientState(Component):
    template_name = "with_alpine.html"

    def get_client_state(self) -> dict:
        return {"open": False}


class Wrapper(Component):
    template_name = "wrapper.html"


class NoStyles(Component):
    label = Prop(str, default="")
    scoped_styles = False
    template_name = "minimal.html"
