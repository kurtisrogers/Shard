from __future__ import annotations

import pytest

from shard.registry import register
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
def instance_id_from_html():
    def _extract(html: str) -> str:
        return html.split('id="shard-')[1].split('"')[0]

    return _extract
