import json
from unittest.mock import patch

import pytest
from django.core.management import call_command

from shard.a11y import A11yViolation, check_html, run_axe_on_html
from shard.a11y_samples import check_rendered_samples, render_view_data_samples

AXE_SAMPLE_VIOLATIONS = [
    {
        "code": "image-alt",
        "message": "Images must have alternative text",
        "impact": "critical",
        "selector": "img",
        "helpUrl": "https://dequeuniversity.com/rules/axe/4.10/image-alt",
        "count": 1,
    }
]


def test_run_axe_on_html_parses_violations():
    with patch("shard.a11y.subprocess.run") as run_mock:
        run_mock.return_value.returncode = 0
        run_mock.return_value.stdout = json.dumps(AXE_SAMPLE_VIOLATIONS)
        run_mock.return_value.stderr = ""

        violations = run_axe_on_html("<img src='x.jpg'>")

    assert len(violations) == 1
    assert violations[0].code == "image-alt"
    assert violations[0].impact == "critical"


def test_check_html_delegates_to_axe():
    with patch("shard.a11y.run_axe_on_html", return_value=[]) as axe_mock:
        assert check_html("<p>ok</p>") == []
    axe_mock.assert_called_once()


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
    assert data["engine"] == "axe-core"
    assert data["count"] == 0


def test_shard_a11y_command_fails_on_violation(capsys):
    def fake_check():
        return [
            (
                "Bad",
                [
                    A11yViolation(
                        code="image-alt",
                        message="Images must have alternative text",
                        selector="img",
                        impact="critical",
                    )
                ],
            )
        ]

    import shard.management.commands.shard_a11y as command_module

    command_module.check_rendered_samples = fake_check
    with pytest.raises(SystemExit) as exc:
        call_command("shard_a11y")
    assert exc.value.code == 1
    assert "image-alt" in capsys.readouterr().err
