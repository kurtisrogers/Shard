import warnings

import pytest
from django.test import Client, override_settings

from shard import TemplateComponent, mount_component
from shard.debug import warn_missing_action
from shard.render import MountResult
from shard.testing import extract_instance_id, post_action
from tests.support.components import Stateful


def test_extract_instance_id_from_html():
    result = mount_component(Stateful, props={"count": 1})
    assert extract_instance_id(result.html) == result.instance_id


def test_extract_instance_id_raises_for_invalid_html():
    with pytest.raises(ValueError, match="does not contain"):
        extract_instance_id("<div>no shard id</div>")


def test_post_action_hits_htmx_endpoint(client: Client):
    result = mount_component(Stateful, props={"count": 2})
    response = post_action(client, result.instance_id, "bump")
    assert response.status_code == 200
    assert ">3<" in response.content.decode()


def test_mount_component_returns_metadata():
    result = mount_component(Stateful, props={"count": 4})
    assert isinstance(result, MountResult)
    assert result.instance_id
    assert result.component.state["value"] == 4
    assert 'id="shard-' in result.html


def test_template_component_exported_from_shard():
    assert issubclass(TemplateComponent, object)


@override_settings(DEBUG=True)
def test_warn_missing_action_emits_warning():
    component = Stateful(props={"count": 0})
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        warn_missing_action(component, "missing", source="test")
    assert any("missing" in str(item.message) for item in caught)


@override_settings(DEBUG=False)
def test_warn_missing_action_silent_outside_debug():
    component = Stateful(props={"count": 0})
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        warn_missing_action(component, "missing", source="test")
    assert caught == []


def test_shard_htmx_warns_on_unknown_action_in_debug():
    from django.template import Context, Template

    component = Stateful(props={"count": 0})
    template = Template("{% load shard %}<button {% shard_htmx component 'missing' %}></button>")
    with override_settings(DEBUG=True):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            html = template.render(Context({"component": component}))
    assert "hx-post=" not in html
    assert any("missing" in str(item.message) for item in caught)
