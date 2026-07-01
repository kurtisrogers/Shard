from django.template import Context, Template

from tests.support.components import Minimal, Stateful


def test_shard_root_tag_renders_attributes():
    component = Minimal(props={"label": "x"})
    template = Template("{% load shard %}<div {% shard_root component %}></div>")
    html = template.render(Context({"component": component}))
    assert f"shard-{component.instance_id}" in html
    assert "data-shard-scope" in html


def test_shard_htmx_tag_renders_post_attrs():
    component = Stateful(props={"count": 0})
    template = Template("{% load shard %}<button {% shard_htmx component 'bump' %}></button>")
    html = template.render(Context({"component": component}))
    assert "hx-post=" in html
    assert "hx-target=" in html


def test_shard_alpine_tag():
    from tests.support.components import WithClientState

    component = WithClientState()
    template = Template("{% load shard %}<div {% shard_alpine component %}></div>")
    html = template.render(Context({"component": component}))
    assert "x-data=" in html


def test_component_block_tag_renders_slot():
    template = Template(
        "{% load shard %}"
        "{% component Minimal label='hi' %}"
        "  <strong>slot</strong>"
        "{% endcomponent %}"
    )
    html = template.render(Context({}))
    assert "hi:" in html
    assert "<strong>slot</strong>" in html


def test_named_slot_block_tag():
    template = Template(
        "{% load shard %}"
        "{% component Wrapper %}"
        "  {% slot default %}main{% endslot %}"
        "{% endcomponent %}"
    )
    html = template.render(Context({}))
    assert "main" in html


def test_shard_child_tag():
    template = Template(
        "{% load shard %}"
        "{% component Wrapper %}"
        "  {% shard_child 'Minimal' label='nested' %}"
        "{% endcomponent %}"
    )
    html = template.render(Context({}))
    assert "nested:" in html


def test_shard_scripts_includes_assets():
    template = Template("{% load shard %}{% shard_scripts alpine=True %}")
    html = template.render(Context({}))
    assert "htmx.min.js" in html
    assert "alpine.min.js" in html
