import pytest

from shard import Component, Prop, mount
from shard.exceptions import PropValidationError
from shard.props import Prop as PropClass
from shard.props import coerce


class TypedComponent(Component):
    name = Prop(str, required=True)
    count = Prop(int, default=0)
    active = Prop(bool, default=False)
    tags = Prop(list[str], default=[])

    template_name = "minimal.html"


def test_prop_descriptor_returns_resolved_value():
    component = TypedComponent(props={"name": "Ada", "count": 3})
    assert component.name == "Ada"
    assert component.count == 3


def test_prop_defaults_apply():
    component = TypedComponent(props={"name": "Ada"})
    assert component.count == 0
    assert component.active is False
    assert component.tags == []


def test_prop_bool_coercion():
    component = TypedComponent(props={"name": "x", "active": "true"})
    assert component.active is True

    component = TypedComponent(props={"name": "x", "active": "0"})
    assert component.active is False


def test_prop_list_coercion_from_json_string():
    assert coerce(list[str], '["a", "b"]') == ["a", "b"]
    component = TypedComponent(props={"name": "x", "tags": ["a", "b"]})
    assert component.tags == ["a", "b"]


def test_required_prop_missing_raises():
    with pytest.raises(PropValidationError, match="name"):
        TypedComponent(props={})


def test_unknown_prop_raises():
    with pytest.raises(PropValidationError, match="colour"):
        TypedComponent(props={"name": "x", "colour": "red"})


def test_invalid_prop_type_raises():
    with pytest.raises(PropValidationError, match="count"):
        TypedComponent(props={"name": "x", "count": "not-a-number"})


def test_coerce_preserves_matching_type():
    assert coerce(int, 5) == 5
    assert coerce(str, "hi") == "hi"


def test_prop_resolve_empty_string_uses_default():
    prop = PropClass(int, default=7)
    prop.name = "n"
    assert prop.resolve("") == 7
    assert prop.resolve(None) == 7


def test_mount_passes_props_to_template():
    from tests.support.components import Minimal

    html = mount(Minimal, props={"label": "world"})
    assert "world:" in html
