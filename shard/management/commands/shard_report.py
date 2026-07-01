import json
import sys

from django.core.management.base import BaseCommand

from shard.weight import build_report, check_budget, format_report, report_as_dict


class Command(BaseCommand):
    help = "Report Shard framework size and page-load weight."

    def add_arguments(self, parser):
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output machine-readable JSON.",
        )
        parser.add_argument(
            "--check-budget",
            action="store_true",
            help="Exit with code 1 if bundled assets exceed size budgets.",
        )

    def handle(self, *args, **options):
        report = build_report()
        violations = check_budget(report) if options["check_budget"] else []

        if options["json"]:
            payload = report_as_dict(report)
            if options["check_budget"]:
                payload["budget_violations"] = violations
            self.stdout.write(json.dumps(payload, indent=2))
            if violations:
                sys.exit(1)
            return

        self.stdout.write(format_report(report))

        if violations:
            self.stderr.write(self.style.ERROR("\nSize budget violations:"))
            for violation in violations:
                self.stderr.write(self.style.ERROR(f"  - {violation}"))
            sys.exit(1)
