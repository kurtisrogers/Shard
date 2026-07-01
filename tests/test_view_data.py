"""Tests for the view-data layout spike."""

import json
import re

import pytest
from django.test import Client

from example.view_data import DEMO_VIEW_DATA, ViewDataError, render_view_data

pytestmark = pytest.mark.django_db


def test_render_view_data_builds_layout_with_nested_components():
    html = str(render_view_data(DEMO_VIEW_DATA))

    assert "layout__header" in html
    assert "layout__main" in html
    assert "layout__footer" in html
    assert "This page was built from view data." in html
    assert "Current count is 3" in html
    assert "Primary action" in html
    assert "View-data spike" in html


def test_render_view_data_rejects_unknown_component():
    node = {"component": "NotRegistered", "props": {}}

    with pytest.raises(ViewDataError, match="not allowed"):
        render_view_data(node)


def test_render_view_data_rejects_missing_component_name():
    with pytest.raises(ViewDataError, match="requires a 'component' name"):
        render_view_data({})


def test_dynamic_page_renders(client: Client):
    response = client.get("/dynamic/")
    body = response.content.decode()

    assert response.status_code == 200
    assert "This page was built from view data." in body
    assert "Current count is 3" in body
    assert "Primary action" in body


def test_dynamic_counter_htmx_action_round_trip(client: Client):
    response = client.get("/dynamic/")
    body = response.content.decode()

    match = re.search(r'id="shard-([^"]+)"[^>]*class="counter"', body)
    assert match is not None
    instance_id = match.group(1)

    action_response = client.post(
        f"/shard/action/{instance_id}/increment/",
        HTTP_HX_REQUEST="true",
    )
    assert action_response.status_code == 200
    assert "Current count is 5" in action_response.content.decode()

    events = json.loads(action_response["HX-Trigger"])
    assert events["counter:changed"] is True


def test_view_data_card_children_use_default_slot():
    node = {
        "component": "Card",
        "props": {"title": "Wrapped"},
        "children": [
            {"component": "Button", "props": {"variant": "primary"}, "content": "Go"},
        ],
    }
    html = str(render_view_data(node))

    assert "card__header" in html
    assert "Go" in html
