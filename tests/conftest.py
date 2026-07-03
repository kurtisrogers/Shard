from __future__ import annotations

import pytest

from shard.registry import register
from shard.testing import extract_instance_id
from tests.support.components import (
    Minimal,
    NoStyles,
    Stateful,
    WithClientState,
    WithComputed,
    WithEvents,
    WithHooks,
    Wrapper,
)


@pytest.fixture(autouse=True)
def register_test_components():
    """Register isolated test components for each test."""

    for component_cls in (
        Minimal,
        Stateful,
        WithComputed,
        WithHooks,
        WithEvents,
        WithClientState,
        Wrapper,
        NoStyles,
    ):
        register(component_cls)
    yield


@pytest.fixture
def shard_instance_id():
    return extract_instance_id
