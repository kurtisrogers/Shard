from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_AXE_SCRIPT = _REPO_ROOT / "scripts" / "axe_check.mjs"


@dataclass(frozen=True)
class A11yViolation:
    code: str
    message: str
    selector: str
    impact: str = ""
    help_url: str = ""


def _ensure_node_dependencies() -> None:
    if shutil.which("node") is None:
        raise RuntimeError(
            "Node.js is required for axe accessibility checks. "
            "Install Node.js and run `npm ci` in your project root."
        )

    if not (_REPO_ROOT / "node_modules" / "axe-core").is_dir():
        if shutil.which("npm") is None:
            raise RuntimeError("npm is required to install axe-core. Run `npm ci` in the project root.")
        subprocess.run(["npm", "ci"], cwd=_REPO_ROOT, check=True, capture_output=True, text=True)


def run_axe_on_html(html: str) -> list[A11yViolation]:
    """Run axe-core against rendered HTML via the Node/jsdom helper script."""

    _ensure_node_dependencies()

    completed = subprocess.run(
        ["node", str(_AXE_SCRIPT)],
        input=html,
        capture_output=True,
        text=True,
        check=False,
        cwd=_REPO_ROOT,
    )

    if completed.returncode != 0 and not completed.stdout.strip():
        stderr = completed.stderr.strip() or "axe check failed"
        raise RuntimeError(stderr)

    raw = json.loads(completed.stdout or "[]")
    return [
        A11yViolation(
            code=item["code"],
            message=item["message"],
            selector=item.get("selector", item["code"]),
            impact=item.get("impact", ""),
            help_url=item.get("helpUrl", ""),
        )
        for item in raw
    ]


def check_html(html: str, *, context: str = "fragment") -> list[A11yViolation]:
    """Return axe accessibility violations for rendered HTML."""

    del context  # axe wrapper handles fragments and documents.
    return run_axe_on_html(html)


def check_template_source(source: str, *, path: str = "<template>") -> list[A11yViolation]:
    """Render-free template checks are not supported with axe.

    Template tags must be rendered before axe can analyze markup. Use
    ``shard_a11y`` without template paths, or add the component to
    ``SHARD_A11Y_COMPONENT_SAMPLES``.
    """

    del source, path
    return []


def format_violations(violations: list[A11yViolation]) -> str:
    if not violations:
        return "No accessibility violations found."

    lines = ["Accessibility violations (axe-core):"]
    for violation in violations:
        impact = f" ({violation.impact})" if violation.impact else ""
        lines.append(f"  [{violation.code}]{impact} {violation.selector}: {violation.message}")
        if violation.help_url:
            lines.append(f"    {violation.help_url}")
    return "\n".join(lines)
