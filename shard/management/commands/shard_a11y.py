import json
import sys

from django.core.management.base import BaseCommand

from shard.a11y import format_violations
from shard.a11y_samples import check_rendered_samples


class Command(BaseCommand):
    help = "Check rendered Shrd components and view-data output for accessibility issues."

    def add_arguments(self, parser):
        parser.add_argument(
            "paths",
            nargs="*",
            help="Ignored for axe checks — templates are validated via rendered samples.",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output machine-readable JSON.",
        )

    def handle(self, *args, **options):
        findings = check_rendered_samples()
        all_findings = findings
        total = sum(len(violations) for _, violations in all_findings)

        if options["json"]:
            payload = {
                "engine": "axe-core",
                "violations": [
                    {
                        "sample": sample,
                        "issues": [
                            {
                                "code": issue.code,
                                "selector": issue.selector,
                                "message": issue.message,
                                "impact": issue.impact,
                                "help_url": issue.help_url,
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
