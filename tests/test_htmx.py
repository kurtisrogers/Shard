from shard.htmx import build_alpine_data, build_htmx_attrs
from tests.support.components import Stateful, WithClientState


def test_build_htmx_attrs_defaults():
    component = Stateful(props={"count": 0})
    attrs = build_htmx_attrs(component, "bump")
    assert 'hx-post="/shard/action/' in attrs
    assert f'hx-target="#shard-{component.instance_id}"' in attrs
    assert 'hx-swap="outerHTML"' in attrs


def test_build_htmx_attrs_custom_options():
    component = Stateful(props={"count": 0})
    attrs = build_htmx_attrs(
        component,
        "bump",
        swap="innerHTML",
        target="#custom",
        trigger="click",
        vals={"key": "val"},
    )
    assert 'hx-swap="innerHTML"' in attrs
    assert 'hx-target="#custom"' in attrs
    assert 'hx-trigger="click"' in attrs
    assert "hx-vals=" in attrs


def test_build_htmx_attrs_unknown_action_returns_empty():
    component = Stateful(props={"count": 0})
    assert build_htmx_attrs(component, "nope") == ""


def test_build_alpine_data_from_client_state():
    component = WithClientState()
    attrs = build_alpine_data(component)
    assert "x-data=" in attrs
    assert "open" in attrs
    assert "false" in attrs


def test_build_alpine_data_merges_extra():
    component = WithClientState()
    attrs = build_alpine_data(component, {"tab": "home"})
    assert "open" in attrs
    assert "tab" in attrs
    assert "home" in attrs
