import json

import pytest
from django.core.management import call_command

from shard.a11y import A11yViolation, check_html, check_template_source
from shard.a11y_samples import check_rendered_samples, render_view_data_samples


def test_check_html_flags_missing_alt():
    violations = check_html('<img src="/logo.png">')
    assert any(v.code == "missing-alt" for v in violations)


def test_check_html_allows_decorative_alt():
    violations = check_html('<img src="/logo.png" alt="">')
    assert violations == []


def test_check_html_flags_unlabeled_input():
    violations = check_html('<input type="text" name="q">')
    assert any(v.code == "missing-label" for v in violations)


def test_check_html_allows_aria_label_input():
    violations = check_html('<input type="text" name="q" aria-label="Search">')
    assert violations == []


def test_check_html_flags_duplicate_ids():
    violations = check_html('<div id="x"></div><span id="x"></span>')
    assert any(v.code == "duplicate-id" for v in violations)


def test_check_html_flags_missing_lang_on_document():
    violations = check_html("<html><body></body></html>", context="document")
    assert any(v.code == "missing-lang" for v in violations)


def test_check_template_source_flags_single_line_img():
    violations = check_template_source('<img src="x">', path="card.html")
    assert any(v.code == "missing-alt" for v in violations)


def test_rendered_example_samples_pass():
    findings = check_rendered_samples()
    assert findings == [], f"Unexpected a11y findings: {findings}"


def test_view_data_sample_renders_for_a11y():
    samples = render_view_data_samples()
    assert samples
    assert any(name == "example.demo_view_tree" for name, _ in samples)


def test_shard_a11y_command_passes(capsys):
    call_command("shard_a11y")
    assert "No accessibility violations" in capsys.readouterr().out


def test_shard_a11y_command_json(capsys):
    call_command("shard_a11y", "--json")
    data = json.loads(capsys.readouterr().out)
    assert data["count"] == 0


def test_shard_a11y_command_fails_on_violation(capsys):
    def fake_check():
        return [
            (
                "Bad",
                [
                    A11yViolation(
                        code="missing-alt",
                        message="missing",
                        selector="img",
                    )
                ],
            )
        ]

    import shard.management.commands.shard_a11y as command_module

    command_module.check_rendered_samples = fake_check
    with pytest.raises(SystemExit) as exc:
        call_command("shard_a11y")
    assert exc.value.code == 1
    assert "Bad" in capsys.readouterr().err
