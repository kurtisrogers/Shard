import json
import sys
from pathlib import Path

from django.core.management.base import BaseCommand

from shard.a11y import check_template_source, format_violations
from shard.a11y_samples import check_rendered_samples


class Command(BaseCommand):
    help = "Check rendered Shrd components and view-data output for accessibility issues."

    def add_arguments(self, parser):
        parser.add_argument(
            "paths",
            nargs="*",
            help="Optional template paths for lightweight static checks.",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output machine-readable JSON.",
        )

    def handle(self, *args, **options):
        findings = check_rendered_samples()
        template_findings: list[tuple[str, list]] = []

        for path_str in options["paths"]:
            path = Path(path_str)
            if not path.is_file() or path.suffix != ".html":
                continue
            source = path.read_text(encoding="utf-8")
            violations = check_template_source(source, path=str(path))
            if violations:
                template_findings.append((str(path), violations))

        all_findings = [*findings, *template_findings]
        total = sum(len(violations) for _, violations in all_findings)

        if options["json"]:
            payload = {
                "violations": [
                    {
                        "sample": sample,
                        "issues": [
                            {
                                "code": issue.code,
                                "selector": issue.selector,
                                "message": issue.message,
                            }
                            for issue in issues
                        ],
                    }
                    for sample, issues in all_findings
                ],
                "count": total,
            }
            self.stdout.write(json.dumps(payload, indent=2))
            if total:
                sys.exit(1)
            return

        if not all_findings:
            self.stdout.write(self.style.SUCCESS("No accessibility violations found."))
            return

        for sample, violations in all_findings:
            self.stderr.write(self.style.ERROR(f"\n{sample}:"))
            self.stderr.write(self.style.ERROR(format_violations(violations)))

        self.stderr.write(self.style.ERROR(f"\n{total} accessibility violation(s) found."))
        sys.exit(1)
