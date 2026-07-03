import pytest

from shard import ActionResult, mount
from shard.exceptions import ActionNotFoundError
from tests.support.components import Stateful, WithComputed, WithEvents, WithHooks


def test_get_initial_state_uses_props():
    html = mount(Stateful, props={"count": 9})
    assert ">9<" in html


def test_dispatch_action_updates_state():
    component = Stateful(props={"count": 1})
    new_state = component.dispatch_action("bump", {})
    assert new_state["value"] == 2


def test_unknown_action_raises():
    component = Stateful(props={"count": 0})
    with pytest.raises(ActionNotFoundError, match="Available actions: bump"):
        component.dispatch_action("missing", {})


def test_computed_available_in_context():
    html = mount(WithComputed, props={"base": 3})
    assert "6" in html


def test_lifecycle_hooks_run():
    component = WithHooks()
    component.dispatch_action("ping", {})
    assert component.state["log"] == ["before:ping", "ping", "after:ping"]


def test_emits_sets_pending_events():
    component = WithEvents()
    component.dispatch_action("tick", {})
    assert component.pending_events["test:tick"] is True


def test_action_result_merges_events():
    component = WithEvents()
    component.dispatch_action("save", {})
    assert component.pending_events["saved"] == {"ok": True}


def test_action_result_redirect():
    component = WithEvents()
    component.dispatch_action("save", {})
    assert component.pending_redirect is None

    result = ActionResult(state={"n": 1}, redirect="/done/")
    state, events, redirect = component._normalize_action_result(result)
    assert redirect == "/done/"
    assert state == {"n": 1}


def test_render_child_from_python():
    from tests.support.components import Minimal, Wrapper

    wrapper = Wrapper(slots={"default": "inner"})
    child_html = wrapper.render_child(Minimal, props={"label": "child"})
    assert "child:" in child_html
