import json

from django.core.management.base import BaseCommand

from shard.weight import build_report, format_report, report_as_dict


class Command(BaseCommand):
    help = "Report Shard framework size and page-load weight."

    def add_arguments(self, parser):
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output machine-readable JSON.",
        )

    def handle(self, *args, **options):
        report = build_report()
        if options["json"]:
            self.stdout.write(json.dumps(report_as_dict(report), indent=2))
            return

        self.stdout.write(format_report(report))
