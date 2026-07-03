import pytest

from shard.exceptions import ComponentNotFoundError
from shard.registry import get_component


def test_get_missing_component_suggests_similar_name():
    with pytest.raises(ComponentNotFoundError, match="Did you mean: Counter"):
        get_component("Countr")


def test_get_missing_component_lists_registry_size():
    with pytest.raises(ComponentNotFoundError, match="registered"):
        get_component("TotallyMissingComponent")
