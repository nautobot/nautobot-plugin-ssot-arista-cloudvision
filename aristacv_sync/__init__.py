"""Plugin declaration for aristacv_sync."""

__version__ = "0.1.0"

from nautobot.extras.plugins import PluginConfig
from django.db.models.signals import post_migrate

class AristaCVSyncConfig(PluginConfig):
    """Plugin configuration for the aristacv_sync plugin."""

    name = "aristacv_sync"
    verbose_name = "Nautobot to Arista CloudVision Sync"
    version = __version__
    author = "Network to Code, LLC"
    description = "Nautobot to Arista CloudVision Sync."
    base_url = "aristacv-sync"
    required_settings = []
    min_version = "1.0.0"
    max_version = "1.9999"
    default_settings = {}
    caching_config = {}

    def ready(self):
        """Callback invoked after the plugin is loaded."""
        super().ready()

        from .signals import (  # pylint: disable=import-outside-toplevel
            post_migrate_create_custom_fields,
        )

        post_migrate.connect(post_migrate_create_custom_fields)



config = AristaCVSyncConfig  # pylint:disable=invalid-name
