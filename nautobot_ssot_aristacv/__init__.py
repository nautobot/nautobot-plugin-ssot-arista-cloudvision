"""Plugin declaration for aristacv_sync."""

try:
    from importlib import metadata
except ImportError:
    # Python version < 3.8
    import importlib_metadata as metadata

__version__ = metadata.version(__name__)

import os

from nautobot.extras.plugins import PluginConfig
from django.db.models.signals import post_migrate


class NautobotSSOTAristaCVConfig(PluginConfig):
    """Plugin configuration for the nautobot_ssot_aristacv plugin."""

    name = "nautobot_ssot_aristacv"
    verbose_name = "Nautobot SSoT Arista CloudVision"
    version = __version__
    author = "Network to Code, LLC"
    description = "Nautobot SSoT Arista CloudVision."
    base_url = "nautobot-sot_aristacv"
    required_settings = []
    min_version = "1.2.0"
    max_version = "1.9999"
    default_settings = {
        "cvp_host": os.getenv("NAUTOBOT_ARISTACV_HOST"),
        "cvp_user": os.getenv("NAUTOBOT_ARISTACV_USERNAME"),
        "cvp_password": os.getenv("NAUTOBOT_ARISTACV_PASSWORD"),
        "verify": os.getenv("NAUTOBOT_ARISTACVP_VERIFY"),
        "cvp_token": os.getenv("NAUTOBOT_ARISTACV_TOKEN"),
    }
    caching_config = {}

    def ready(self):
        """Callback invoked after the plugin is loaded."""
        super().ready()

        from .signals import (  # pylint: disable=import-outside-toplevel
            post_migrate_create_custom_fields,
        )

        post_migrate.connect(post_migrate_create_custom_fields)


config = NautobotSSOTAristaCVConfig  # pylint:disable=invalid-name
