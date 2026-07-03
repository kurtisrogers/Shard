import pytest
from django.core.management import call_command
from django.urls import clear_url_caches


def test_shard_list_verbose_shows_template_details(capsys):
    call_command("shard_list", "--verbose")
    output = capsys.readouterr().out
    assert "template:" in output
    assert "scoped_styles:" in output


def test_shard_list_no_components_message(capsys, monkeypatch):
    monkeypatch.setattr(
        "shard.management.commands.shard_list.get_all_components",
        lambda: {},
    )
    call_command("shard_list")
    assert "No components registered" in capsys.readouterr().out


def test_shard_doctor_passes_in_test_project(capsys):
    call_command("shard_doctor")
    output = capsys.readouterr().out
    assert "All Shard health checks passed" in output


def test_shard_doctor_reports_url_namespace_issue(capsys, monkeypatch):
    monkeypatch.setattr(
        "shard.management.commands.shard_doctor.get_setting",
        lambda name: "missing-namespace",
    )
    clear_url_caches()
    with pytest.raises(SystemExit) as exc:
        call_command("shard_doctor")
    assert exc.value.code == 1
    err = capsys.readouterr()
    assert "does not reverse" in err.out + err.err


def test_shard_doctor_reports_missing_template(capsys, monkeypatch):
    from tests.support.components import Minimal

    class Broken(Minimal):
        template_name = "definitely-missing-template.html"

    monkeypatch.setattr(
        "shard.management.commands.shard_doctor.get_all_components",
        lambda: {"Broken": Broken},
    )
    with pytest.raises(SystemExit):
        call_command("shard_doctor")
    assert "template not found" in capsys.readouterr().out
