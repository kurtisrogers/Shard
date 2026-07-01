import pytest

from shard.exceptions import ComponentNotFoundError
from shard.registry import get_all_components, get_component, register
from tests.support.components import Minimal


def test_register_and_get_component():
    register(Minimal, name="TestMinimal")
    assert get_component("TestMinimal") is Minimal


def test_get_missing_component_raises():
    with pytest.raises(ComponentNotFoundError, match="NotRegistered"):
        get_component("NotRegistered")


def test_get_all_components_includes_example_app():
    names = get_all_components()
    assert "Counter" in names
    assert "Card" in names
