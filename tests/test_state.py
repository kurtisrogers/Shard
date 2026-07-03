import pytest

from shard.exceptions import StateNotFoundError
from shard.state import StateStore


def test_state_store_round_trip():
    StateStore.save(
        instance_id="abc",
        component_name="Counter",
        props={"initial": 1},
        state={"count": 1},
        slots={"default": "<p>Hi</p>"},
    )

    record = StateStore.load("abc")
    assert record.component_name == "Counter"
    assert record.props == {"initial": 1}
    assert record.state == {"count": 1}
    assert record.slots == {"default": "<p>Hi</p>"}


def test_state_store_missing_raises():
    with pytest.raises(StateNotFoundError, match="SHARD_STATE_TIMEOUT"):
        StateStore.load("does-not-exist")


def test_state_store_delete():
    StateStore.save(
        instance_id="temp",
        component_name="X",
        props={},
        state={},
    )
    StateStore.delete("temp")
    with pytest.raises(StateNotFoundError):
        StateStore.load("temp")


def test_slots_persisted_across_save_load():
    StateStore.save(
        instance_id="slots-test",
        component_name="Wrapper",
        props={},
        state={},
        slots={"default": "<em>child</em>"},
    )
    record = StateStore.load("slots-test")
    assert record.slots["default"] == "<em>child</em>"
