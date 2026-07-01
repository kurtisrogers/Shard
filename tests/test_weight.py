import json

import pytest
from django.core.management import call_command
from django.test import Client

from example.components import Counter
from shard import mount
from shard.weight import build_report, report_as_dict


def test_build_report_includes_all_assets():
    report = build_report()
    names = {asset.name for asset in report.assets}
    assert names == {"htmx.min.js", "shard.js", "alpine.min.js"}


def test_required_gzip_smaller_than_with_alpine():
    report = build_report()
    assert report.required_gzip_bytes < report.total_gzip_bytes
    assert report.request_count_required == 2
    assert report.request_count_with_alpine == 3


def test_report_as_dict_structure():
    data = report_as_dict()
    assert "assets" in data
    assert "summary" in data
    assert data["summary"]["required_gzip_bytes"] > 0


def test_shard_report_command(capsys):
    call_command("shard_report")
    output = capsys.readouterr().out
    assert "htmx.min.js" in output
    assert "Page load summary" in output


def test_shard_report_json(capsys):
    call_command("shard_report", "--json")
    output = capsys.readouterr().out
    data = json.loads(output)
    assert data["summary"]["total_gzip_bytes"] > 0


def test_htmx_partial_skips_scoped_styles(client: Client):
    html = mount(Counter, props={"initial": 1, "step": 1})
    assert "<style data-shard-styles=" in html

    instance_id = html.split('id="shard-')[1].split('"')[0]
    response = client.post(
        f"/shard/action/{instance_id}/increment/",
        HTTP_HX_REQUEST="true",
    )
    assert "<style data-shard-styles=" not in response.content.decode()


def test_shard_scripts_excludes_alpine_by_default():
    from django.template import Context, Template

    template = Template("{% load shard %}{% shard_scripts %}")
    html = template.render(Context({}))
    assert "htmx.min.js" in html
    assert "shard.js" in html
    assert "alpine.min.js" not in html


def test_shard_scripts_includes_alpine_when_requested():
    from django.template import Context, Template

    template = Template("{% load shard %}{% shard_scripts alpine=True %}")
    html = template.render(Context({}))
    assert "alpine.min.js" in html
