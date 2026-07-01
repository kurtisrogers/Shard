from django.core.management.base import BaseCommand

from shard.registry import get_all_components


class Command(BaseCommand):
    help = "List registered Shard components."

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
