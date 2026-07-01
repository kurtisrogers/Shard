"""Tests for shard.view_data."""

import pytest

from shard.exceptions import StateNotFoundError, ViewDataError
from shard.state import StateStore
from shard.view_data import (
    collect_node_ids,
    commit_view_tree,
    ensure_node_ids,
    get_slot_nodes,
    prune_orphaned_nodes,
    render_view_data,
    set_slot_nodes,
)

pytestmark = pytest.mark.django_db

TEST_ALLOWED = frozenset({"Minimal", "Stateful", "Wrapper"})


def test_render_view_data_builds_nested_components():
    node = {
        "component": "Wrapper",
        "children": [
            {"component": "Minimal", "props": {"label": "nested"}},
        ],
    }
    html = str(render_view_data(node, allowed_components=TEST_ALLOWED))

    assert "nested" in html


def test_render_view_data_rejects_unknown_component():
    node = {"component": "NotRegistered", "props": {}}

    with pytest.raises(ViewDataError, match="not allowed"):
        render_view_data(node, allowed_components=TEST_ALLOWED)


def test_render_view_data_requires_whitelist(settings):
    settings.SHARD_VIEW_DATA_ALLOWED_COMPONENTS = None

    with pytest.raises(ViewDataError, match="explicit component whitelist"):
        render_view_data({"component": "Minimal", "props": {}})


def test_render_view_data_rejects_missing_component_name():
    with pytest.raises(ViewDataError, match="requires a 'component' name"):
        render_view_data({}, allowed_components=TEST_ALLOWED)


def test_children_render_into_default_slot():
    node = {
        "component": "Wrapper",
        "children": [
            {"component": "Minimal", "props": {"label": "child"}},
        ],
    }
    html = str(render_view_data(node, allowed_components=TEST_ALLOWED))
    assert "child" in html


def test_ensure_node_ids_assigns_ids_recursively():
    tree = ensure_node_ids(
        {
            "component": "Wrapper",
            "children": [{"component": "Minimal", "props": {"label": "x"}}],
        }
    )

    assert tree["id"]
    assert tree["children"][0]["id"]
    assert len(collect_node_ids(tree)) == 2


def test_get_and_set_slot_nodes():
    tree = {
        "component": "Wrapper",
        "slots": {"default": [{"component": "Minimal", "props": {"label": "a"}}]},
    }
    updated = set_slot_nodes(tree, "default", [])

    assert get_slot_nodes(tree, "default")[0]["props"]["label"] == "a"
    assert get_slot_nodes(updated, "default") == []


def test_stable_render_reuses_existing_child_state():
    tree = ensure_node_ids(
        {
            "component": "Stateful",
            "props": {"count": 1},
        }
    )
    counter_id = tree["id"]

    first = str(render_view_data(tree, allowed_components=TEST_ALLOWED, stable=True))
    assert ">1<" in first

    record = StateStore.load(counter_id)
    record_state = dict(record.state)
    record_state["value"] = 9
    StateStore.save(
        instance_id=counter_id,
        component_name=record.component_name,
        props=record.props,
        state=record_state,
        slots=record.slots,
    )

    second = str(render_view_data(tree, allowed_components=TEST_ALLOWED, stable=True))
    assert ">9<" in second


def test_commit_view_tree_prunes_removed_nodes():
    tree = ensure_node_ids(
        {
            "component": "Wrapper",
            "children": [
                {"component": "Minimal", "props": {"label": "keep"}},
                {"component": "Minimal", "props": {"label": "remove"}},
            ],
        }
    )
    render_view_data(tree, allowed_components=TEST_ALLOWED, stable=True)
    removed_id = tree["children"][1]["id"]

    state = {"tree": tree}
    pruned_tree = {
        "component": "Wrapper",
        "id": tree["id"],
        "children": [tree["children"][0]],
    }
    commit_view_tree(state, "tree", pruned_tree)

    with pytest.raises(StateNotFoundError):
        StateStore.load(removed_id)


def test_prune_orphaned_nodes_deletes_cache_entries():
    tree = ensure_node_ids({"component": "Minimal", "props": {"label": "x"}})
    render_view_data(tree, allowed_components=TEST_ALLOWED, stable=True)
    instance_id = tree["id"]

    prune_orphaned_nodes({instance_id})

    with pytest.raises(StateNotFoundError):
        StateStore.load(instance_id)
