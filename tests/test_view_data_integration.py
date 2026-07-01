"""Integration tests for view-data rendering in the example app."""

import json
import re

import pytest
from django.test import Client

from example.demo_view_data import DEMO_VIEW_DATA, EXAMPLE_ALLOWED_COMPONENTS
from shard import render_view_data

pytestmark = pytest.mark.django_db


def test_example_view_data_renders_layout():
    html = str(render_view_data(DEMO_VIEW_DATA, allowed_components=EXAMPLE_ALLOWED_COMPONENTS))

    assert "layout__header" in html
    assert "layout__main" in html
    assert "layout__footer" in html
    assert "This page was built from view data." in html
    assert "Current count is 3" in html
    assert "Primary action" in html
    assert "View data layout" in html


def test_dynamic_page_renders(client: Client):
    response = client.get("/dynamic/")
    body = response.content.decode()

    assert response.status_code == 200
    assert "Add card" in body
    assert "This page was built from view data." in body
    assert "Current count is 3" in body
    assert "Primary action" in body
    assert "3 card(s)" in body


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


def _view_page_id(body: str) -> str:
    match = re.search(r'id="shard-([^"]+)"[^>]*class="view-page"', body)
    assert match is not None
    return match.group(1)


def _counter_id(body: str) -> str:
    match = re.search(r'id="shard-([^"]+)"[^>]*class="counter"', body)
    assert match is not None
    return match.group(1)


def test_view_page_add_card_action(client: Client):
    response = client.get("/dynamic/")
    view_page_id = _view_page_id(response.content.decode())

    action_response = client.post(
        f"/shard/action/{view_page_id}/add_card/",
        HTTP_HX_REQUEST="true",
    )
    body = action_response.content.decode()

    assert action_response.status_code == 200
    assert "Dynamic card 4" in body
    assert "4 card(s)" in body


def test_view_page_preserves_child_state_after_layout_mutation(client: Client):
    response = client.get("/dynamic/")
    body = response.content.decode()
    view_page_id = _view_page_id(body)
    counter_id = _counter_id(body)

    increment = client.post(
        f"/shard/action/{counter_id}/increment/",
        HTTP_HX_REQUEST="true",
    )
    assert "Current count is 5" in increment.content.decode()

    add_card = client.post(
        f"/shard/action/{view_page_id}/add_card/",
        HTTP_HX_REQUEST="true",
    )
    body = add_card.content.decode()

    assert "Dynamic card 4" in body
    assert "Current count is 5" in body


def test_view_page_toggle_footer_action(client: Client):
    response = client.get("/dynamic/")
    view_page_id = _view_page_id(response.content.decode())

    assert "View data layout" in response.content.decode()

    hidden = client.post(
        f"/shard/action/{view_page_id}/toggle_footer/",
        HTTP_HX_REQUEST="true",
    )
    body = hidden.content.decode()
    assert "View data layout" not in body
    assert "layout__footer" in body

    restored = client.post(
        f"/shard/action/{view_page_id}/toggle_footer/",
        HTTP_HX_REQUEST="true",
    )
    body = restored.content.decode()
    assert "Footer restored from view-data state." in body


def test_view_page_remove_last_card_prunes_added_card(client: Client):
    response = client.get("/dynamic/")
    view_page_id = _view_page_id(response.content.decode())

    add_card = client.post(
        f"/shard/action/{view_page_id}/add_card/",
        HTTP_HX_REQUEST="true",
    )
    assert "Dynamic card 4" in add_card.content.decode()

    remove_card = client.post(
        f"/shard/action/{view_page_id}/remove_last_card/",
        HTTP_HX_REQUEST="true",
    )
    body = remove_card.content.decode()

    assert "Dynamic card 4" not in body
    assert "3 card(s)" in body
