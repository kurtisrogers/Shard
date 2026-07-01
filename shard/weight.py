from __future__ import annotations

import gzip
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AssetSize:
    name: str
    path: str
    raw_bytes: int
    gzip_bytes: int
    required: bool

    @property
    def gzip_kb(self) -> float:
        return self.gzip_bytes / 1024


@dataclass(frozen=True)
class WeightReport:
    assets: tuple[AssetSize, ...]
    python_module_bytes: int

    @property
    def required_raw_bytes(self) -> int:
        return sum(asset.raw_bytes for asset in self.assets if asset.required)

    @property
    def required_gzip_bytes(self) -> int:
        return sum(asset.gzip_bytes for asset in self.assets if asset.required)

    @property
    def optional_gzip_bytes(self) -> int:
        return sum(asset.gzip_bytes for asset in self.assets if not asset.required)

    @property
    def total_gzip_bytes(self) -> int:
        return sum(asset.gzip_bytes for asset in self.assets)

    @property
    def request_count_required(self) -> int:
        return sum(1 for asset in self.assets if asset.required)

    @property
    def request_count_with_alpine(self) -> int:
        return len(self.assets)


@dataclass(frozen=True)
class BudgetLimits:
    asset_gzip_bytes: dict[str, int]
    required_gzip_bytes: int
    total_gzip_bytes: int


# Headroom above current shipped sizes; CI fails if assets grow past these limits.
DEFAULT_BUDGETS = BudgetLimits(
    asset_gzip_bytes={
        "htmx.min.js": 17_500,
        "shard.js": 500,
        "alpine.min.js": 17_500,
    },
    required_gzip_bytes=18_000,
    total_gzip_bytes=35_000,
)


ASSET_DEFINITIONS: tuple[tuple[str, bool], ...] = (
    ("js/htmx.min.js", True),
    ("js/shard.js", True),
    ("js/alpine.min.js", False),
)


def _static_root() -> Path:
    return Path(__file__).resolve().parent / "static" / "shard"


def _gzip_size(data: bytes) -> int:
    return len(gzip.compress(data))


def measure_asset(relative_path: str, *, required: bool) -> AssetSize:
    path = _static_root() / relative_path
    raw = path.read_bytes()
    return AssetSize(
        name=path.name,
        path=f"shard/static/shard/{relative_path}",
        raw_bytes=len(raw),
        gzip_bytes=_gzip_size(raw),
        required=required,
    )


def measure_python_package() -> int:
    total = 0
    package_root = Path(__file__).resolve().parent
    for path in package_root.rglob("*"):
        if path.is_file() and path.suffix in {".py", ".html", ".js", ".css"}:
            total += path.stat().st_size
    return total


def build_report() -> WeightReport:
    assets = tuple(
        measure_asset(relative_path, required=required)
        for relative_path, required in ASSET_DEFINITIONS
    )
    return WeightReport(assets=assets, python_module_bytes=measure_python_package())


def format_report(report: WeightReport | None = None) -> str:
    report = report or build_report()
    lines = [
        "Shard framework weight",
        "",
        "Client assets (transfer size is gzip over the wire):",
        "",
        f"{'Asset':<16} {'Raw':>10} {'Gzip':>10}  Load",
        f"{'-' * 16} {'-' * 10} {'-' * 10}  ----",
    ]

    for asset in report.assets:
        load = "required" if asset.required else "optional"
        lines.append(f"{asset.name:<16} {asset.raw_bytes:>8,} B {asset.gzip_bytes:>8,} B  {load}")

    lines.extend(
        [
            "",
            "Page load summary:",
            f"  HTMX only:     {report.required_gzip_bytes:,} B gzip, "
            f"{report.request_count_required} requests",
            f"  + Alpine.js:   {report.total_gzip_bytes:,} B gzip, "
            f"{report.request_count_with_alpine} requests",
            "",
            "Server footprint:",
            f"  Python package (code/templates): {report.python_module_bytes:,} B",
            "  Runtime deps: Django cache only (no extra DB tables)",
            "",
            "Tips:",
            "  - Use {% shard_scripts %} without Alpine unless you need client state",
            "  - Scoped CSS is omitted from HTMX partial responses after first render",
            "  - Component CSS is minified by default (SHARD_MINIFY_CSS)",
            "  - HTMX/shard.js preload hints are enabled by default (SHARD_PRELOAD_SCRIPTS)",
            "  - Run with --json for machine-readable output",
            "  - Run with --check-budget to fail CI when assets exceed limits",
        ]
    )
    return "\n".join(lines)


def check_budget(
    report: WeightReport | None = None,
    budgets: BudgetLimits | None = None,
) -> list[str]:
    report = report or build_report()
    budgets = budgets or DEFAULT_BUDGETS
    violations: list[str] = []

    for asset in report.assets:
        limit = budgets.asset_gzip_bytes.get(asset.name)
        if limit is not None and asset.gzip_bytes > limit:
            violations.append(
                f"{asset.name}: {asset.gzip_bytes:,} B gzip exceeds budget of {limit:,} B"
            )

    if report.required_gzip_bytes > budgets.required_gzip_bytes:
        violations.append(
            "Required JS total: "
            f"{report.required_gzip_bytes:,} B gzip exceeds budget of "
            f"{budgets.required_gzip_bytes:,} B"
        )

    if report.total_gzip_bytes > budgets.total_gzip_bytes:
        violations.append(
            "Total JS: "
            f"{report.total_gzip_bytes:,} B gzip exceeds budget of "
            f"{budgets.total_gzip_bytes:,} B"
        )

    return violations


def budgets_as_dict(budgets: BudgetLimits | None = None) -> dict:
    budgets = budgets or DEFAULT_BUDGETS
    return {
        "asset_gzip_bytes": dict(budgets.asset_gzip_bytes),
        "required_gzip_bytes": budgets.required_gzip_bytes,
        "total_gzip_bytes": budgets.total_gzip_bytes,
    }


def report_as_dict(report: WeightReport | None = None) -> dict:
    report = report or build_report()
    return {
        "assets": [
            {
                "name": asset.name,
                "path": asset.path,
                "raw_bytes": asset.raw_bytes,
                "gzip_bytes": asset.gzip_bytes,
                "required": asset.required,
            }
            for asset in report.assets
        ],
        "summary": {
            "required_raw_bytes": report.required_raw_bytes,
            "required_gzip_bytes": report.required_gzip_bytes,
            "optional_gzip_bytes": report.optional_gzip_bytes,
            "total_gzip_bytes": report.total_gzip_bytes,
            "request_count_required": report.request_count_required,
            "request_count_with_alpine": report.request_count_with_alpine,
            "python_module_bytes": report.python_module_bytes,
        },
        "budgets": budgets_as_dict(),
    }
