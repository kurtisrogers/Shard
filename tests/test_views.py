import json

from django.test import Client

from shard import mount
from tests.support.components import NoStyles, Stateful, Wrapper


def test_action_requires_htmx_header(client: Client):
    html = mount(Stateful, props={"count": 0})
    instance_id = html.split('id="shard-')[1].split('"')[0]

    response = client.post(f"/shard/action/{instance_id}/bump/")
    assert response.status_code == 400


def test_action_unknown_instance_returns_404(client: Client):
    response = client.post(
        "/shard/action/missing-id/bump/",
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 404


def test_action_unknown_action_returns_404(client: Client):
    html = mount(Stateful, props={"count": 0})
    instance_id = html.split('id="shard-')[1].split('"')[0]

    response = client.post(
        f"/shard/action/{instance_id}/not-real/",
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 404


def test_action_success_returns_html_fragment(client: Client):
    html = mount(Stateful, props={"count": 2})
    instance_id = html.split('id="shard-')[1].split('"')[0]

    response = client.post(
        f"/shard/action/{instance_id}/bump/",
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 200
    assert ">3<" in response.content.decode()


def test_action_includes_trigger_header(client: Client):
    html = mount(Stateful, props={"count": 0})
    instance_id = html.split('id="shard-')[1].split('"')[0]

    response = client.post(
        f"/shard/action/{instance_id}/bump/",
        HTTP_HX_REQUEST="true",
    )
    events = json.loads(response["HX-Trigger"])
    assert events["shard:action-complete"] is True


def test_render_endpoint_returns_component(client: Client):
    html = mount(Stateful, props={"count": 7})
    instance_id = html.split('id="shard-')[1].split('"')[0]

    response = client.get(f"/shard/render/{instance_id}/")
    assert response.status_code == 200
    assert ">7<" in response.content.decode()


def test_render_missing_instance_returns_404(client: Client):
    response = client.get("/shard/render/missing/")
    assert response.status_code == 404


def test_slots_survive_action_rerender(client: Client):
    html = mount(Wrapper, slots={"default": "<b>kept</b>"})
    instance_id = html.split('id="shard-')[1].split('"')[0]

    # Wrapper has no actions; use render endpoint to simulate re-render
    response = client.get(f"/shard/render/{instance_id}/")
    assert "<b>kept</b>" in response.content.decode()


def test_scoped_styles_disabled():
    html = mount(NoStyles, props={"label": "plain"})
    assert "<style data-shard-styles=" not in html
