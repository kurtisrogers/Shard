"""Integration tests against the example application."""

import json

import pytest
from django.core.management import call_command
from django.test import Client

from example.components import Alert, Button, Counter, Layout, TodoList
from shard import mount
from shard.slots import SlotContent

pytestmark = pytest.mark.django_db


def test_example_counter_action_updates_state(client: Client):
    html = mount(Counter, props={"initial": 1, "step": 2})
    instance_id = html.split('id="shard-')[1].split('"')[0]

    response = client.post(
        f"/shard/action/{instance_id}/increment/",
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 200
    assert "Current count is 3" in response.content.decode()

    events = json.loads(response["HX-Trigger"])
    assert events["counter:changed"] is True


def test_example_todo_add_item(client: Client):
    html = mount(TodoList, props={"placeholder": "Task"})
    instance_id = html.split('id="shard-')[1].split('"')[0]

    response = client.post(
        f"/shard/action/{instance_id}/add_item/",
        data={"text": "Write tests"},
        HTTP_HX_REQUEST="true",
    )
    assert "Write tests" in response.content.decode()


def test_example_home_page_renders(client: Client):
    response = client.get("/")
    body = response.content.decode()
    assert response.status_code == 200
    assert "Shard" in body
    assert "Primary action" in body


def test_example_layout_and_wrappers():
    html = mount(
        Layout,
        slots={
            "header": "<h1>H</h1>",
            "default": "<p>Body</p>",
            "footer": "<small>F</small>",
        },
    )
    assert "H" in html and "Body" in html and "F" in html

    html = mount(Button, slots={"default": "Go"}, props={"variant": "primary"})
    assert "Go" in html

    html = mount(Alert, props={"level": "success"}, slots={"default": "Done"})
    assert "alert--success" in html


def test_shard_list_command(capsys):
    call_command("shard_list")
    output = capsys.readouterr().out
    assert "Counter" in output
    assert "increment" in output


def test_slot_content_helpers():
    slots = SlotContent()
    assert slots.get("default") == ""

    slots = SlotContent.from_mapping({"default": "<b>x</b>"})
    assert slots.get("default") == "<b>x</b>"
