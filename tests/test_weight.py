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
    assert "budgets" in data
    assert data["summary"]["required_gzip_bytes"] > 0


def test_check_budget_passes_for_current_assets():
    from shard.weight import check_budget

    assert check_budget() == []


def test_check_budget_detects_violation():
    from shard.weight import BudgetLimits, build_report, check_budget

    report = build_report()
    tight = BudgetLimits(
        asset_gzip_bytes={"htmx.min.js": 1},
        required_gzip_bytes=1,
        total_gzip_bytes=1,
    )
    violations = check_budget(report, budgets=tight)
    assert violations
    assert any("htmx.min.js" in violation for violation in violations)


def test_shard_report_check_budget_passes(capsys):
    call_command("shard_report", "--check-budget")
    output = capsys.readouterr()
    assert output.err == ""


def test_shard_report_check_budget_json(capsys):
    call_command("shard_report", "--json", "--check-budget")
    output = capsys.readouterr().out
    data = json.loads(output)
    assert data["budget_violations"] == []


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
    assert "budgets" in data


@pytest.mark.parametrize("flag", ["--check-budget"])
def test_shard_report_check_budget_fails_on_violation(flag, monkeypatch, capsys):
    monkeypatch.setattr(
        "shard.management.commands.shard_report.check_budget",
        lambda report=None, budgets=None: ["htmx.min.js: too large"],
    )
    with pytest.raises(SystemExit) as exc:
        call_command("shard_report", flag)
    assert exc.value.code == 1
    assert "htmx.min.js" in capsys.readouterr().err


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
    assert 'rel="preload"' in html
    assert html.count('rel="preload"') == 2


def test_shard_scripts_includes_alpine_when_requested():
    from django.template import Context, Template

    template = Template("{% load shard %}{% shard_scripts alpine=True %}")
    html = template.render(Context({}))
    assert "alpine.min.js" in html
    assert html.count('rel="preload"') == 3


def test_shard_scripts_can_disable_preload():
    from django.template import Context, Template
    from django.test import override_settings

    template = Template("{% load shard %}{% shard_scripts %}")
    with override_settings(SHARD_PRELOAD_SCRIPTS=False):
        html = template.render(Context({}))
    assert 'rel="preload"' not in html
