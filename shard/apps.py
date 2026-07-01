from django.apps import AppConfig


class ShardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shard"
    verbose_name = "Shard Component Framework"

    def ready(self) -> None:
        from shard.registry import autodiscover_components

        autodiscover_components()
