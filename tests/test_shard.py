import pytest
from django.test import Client, override_settings

from example.components import Button, Card, Counter
from shard import mount
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


def test_counter_action_updates_state(client: Client):
    html = mount(Counter, props={"initial": 1, "step": 2})
    instance_id = html.split('id="shard-')[1].split('"')[0]

    response = client.post(
        f"/shard/action/{instance_id}/increment/",
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 200
    assert "Count:" in response.content.decode()
    assert ">3<" in response.content.decode()


def test_template_block_component_renders_slots(client: Client):
    response = client.get("/")
    body = response.content.decode()
    assert "Shard" in body
    assert "Wrapped actions" in body
    assert "Primary action" in body


def test_slot_content_defaults():
    slots = SlotContent()
    assert slots.get("default") == ""

    slots = SlotContent.from_mapping({"default": "<b>x</b>"})
    assert slots.get("default") == "<b>x</b>"
