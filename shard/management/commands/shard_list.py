from django.core.management.base import BaseCommand
from django.template import TemplateDoesNotExist
from django.template.loader import get_template

from shard.registry import get_all_components


class Command(BaseCommand):
    help = "List registered Shard components."

    def add_arguments(self, parser):
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show template, scope, and template-exists details per component.",
        )

    def handle(self, *args, **options):
        components = get_all_components()
        if not components:
            self.stdout.write("No components registered.")
            return

        name_width = max(len(name) for name in components)
        self.stdout.write(f"{'NAME'.ljust(name_width)}  CLASS")
        self.stdout.write("-" * (name_width + 10))

        for name, component_cls in sorted(components.items()):
            props = ", ".join(component_cls.prop_names()) or "—"
            actions = ", ".join(component_cls.action_names()) or "—"
            self.stdout.write(
                f"{name.ljust(name_width)}  {component_cls.__module__}.{component_cls.__name__}"
            )
            self.stdout.write(f"{'':<{name_width}}  props: {props}")
            self.stdout.write(f"{'':<{name_width}}  actions: {actions}")

            if options["verbose"]:
                template_name = component_cls.template_name or "—"
                scope = component_cls.scope or component_cls.component_name
                styles = "yes" if component_cls.scoped_styles else "no"
                self.stdout.write(f"{'':<{name_width}}  template: {template_name}")
                self.stdout.write(f"{'':<{name_width}}  scope: {scope}")
                self.stdout.write(f"{'':<{name_width}}  scoped_styles: {styles}")

                if not component_cls.template_name:
                    self.stdout.write(
                        self.style.WARNING(f"{'':<{name_width}}  warning: missing template_name")
                    )
                else:
                    try:
                        get_template(component_cls.template_name)
                    except TemplateDoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"{'':<{name_width}}  warning: template not found: "
                                f"{component_cls.template_name}"
                            )
                        )
