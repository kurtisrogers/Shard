import json

import pytest
from django.core.management import call_command
from django.test import Client

from example.components import Alert, Button, Card, Counter, Layout, TodoList
from shard import ActionResult, mount
from shard.props import Prop
from shard.scoping import scope_css
from shard.slots import SlotContent


pytestmark = pytest.mark.django_db


def test_scope_css_prefixes_selectors():
    scoped = scope_css(".title { color: red; }", "card")
    assert '[data-shard-scope="card"] .title' in scoped
    assert "color: red" in scoped


def test_scope_css_handles_media_queries():
    css = "@media (max-width: 600px) { .box { padding: 1rem; } }"
    scoped = scope_css(css, "card")
    assert "@media" in scoped
    assert "max-width: 600px" in scoped
    assert '[data-shard-scope="card"] .box' in scoped


def test_component_renders_wrapped_slot():
    html = mount(
        Button,
        slots={"default": "Save changes"},
        props={"variant": "primary"},
    )
    assert "Save changes" in html
    assert 'data-shard-scope="button"' in html
    assert "<style data-shard-styles=" in html


def test_component_renders_card_wrapper():
    html = mount(
        Card,
        props={"title": "Wrapped"},
        slots={"default": "<p>Inner content</p>"},
    )
    assert "Wrapped" in html
    assert "Inner content" in html
    assert 'data-shard-scope="card"' in html


def test_computed_values_in_template():
    html = mount(Alert, props={"message": "Hi", "level": "success"}, slots={"default": "Saved!"})
    assert "alert--success" in html
    assert "Saved!" in html


def test_counter_computed_label():
    html = mount(Counter, props={"initial": 4, "step": 1})
    assert "Current count is 4" in html


def test_counter_action_updates_state(client: Client):
    html = mount(Counter, props={"initial": 1, "step": 2})
    instance_id = html.split('id="shard-')[1].split('"')[0]

    response = client.post(
        f"/shard/action/{instance_id}/increment/",
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 200
    assert "Current count is 3" in response.content.decode()

    events = json.loads(response["HX-Trigger"])
    assert events["shard:action-complete"] is True
    assert events["counter:changed"] is True


def test_action_result_emits_events(client: Client):
    html = mount(TodoList, props={"placeholder": "Task"})
    instance_id = html.split('id="shard-')[1].split('"')[0]

    response = client.post(
        f"/shard/action/{instance_id}/add_item/",
        data={"text": "Write docs"},
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 200
    assert "Write docs" in response.content.decode()

    events = json.loads(response["HX-Trigger"])
    assert "todo:added" in events


def test_template_block_component_renders_slots(client: Client):
    response = client.get("/")
    body = response.content.decode()
    assert "Shard" in body
    assert "Wrapped actions" in body
    assert "Primary action" in body
    assert "layout" in body


def test_layout_named_slots():
    html = mount(
        Layout,
        slots={
            "header": "<h1>Header</h1>",
            "default": "<p>Body</p>",
            "footer": "<small>Footer</small>",
        },
    )
    assert "Header" in html
    assert "Body" in html
    assert "Footer" in html


def test_shard_list_command(capsys):
    call_command("shard_list")
    output = capsys.readouterr().out
    assert "Counter" in output
    assert "increment" in output


def test_slot_content_defaults():
    slots = SlotContent()
    assert slots.get("default") == ""

    slots = SlotContent.from_mapping({"default": "<b>x</b>"})
    assert slots.get("default") == "<b>x</b>"
