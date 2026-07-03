from django.conf import settings
from django.core.management.base import BaseCommand
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import NoReverseMatch, reverse

from shard.conf import get_setting
from shard.registry import get_all_components


class Command(BaseCommand):
    help = "Check Shard project configuration and component health."

    def handle(self, *args, **options):
        issues: list[str] = []
        notes: list[str] = []

        if not hasattr(settings, "CACHES") or "default" not in settings.CACHES:
            issues.append("CACHES['default'] is not configured.")
        else:
            notes.append(f"Cache backend: {settings.CACHES['default']['BACKEND']}")

        namespace = get_setting("URL_NAMESPACE")
        try:
            reverse(f"{namespace}:action", args=["health-check", "ping"])
            notes.append(f"URL namespace '{namespace}' resolves action routes.")
        except NoReverseMatch:
            issues.append(
                f"URL namespace '{namespace}' does not reverse. "
                "Include shard.urls and ensure SHARD_URL_NAMESPACE matches."
            )

        components = get_all_components()
        if not components:
            issues.append("No components registered.")
        else:
            notes.append(f"{len(components)} component(s) registered.")

        for name, component_cls in sorted(components.items()):
            if not component_cls.template_name:
                issues.append(f"{name}: missing template_name.")
                continue
            try:
                get_template(component_cls.template_name)
            except TemplateDoesNotExist:
                issues.append(f"{name}: template not found ({component_cls.template_name}).")

        if notes:
            self.stdout.write("Checks passed:")
            for note in notes:
                self.stdout.write(f"  - {note}")

        if issues:
            self.stdout.write("")
            self.stdout.write(self.style.ERROR("Issues found:"))
            for issue in issues:
                self.stdout.write(self.style.ERROR(f"  - {issue}"))
            self.stderr.write(self.style.ERROR(f"\n{len(issues)} issue(s) found."))
            raise SystemExit(1)

        self.stdout.write(self.style.SUCCESS("\nAll Shard health checks passed."))
