"""Tests that assure specific settings are working correctly."""
from django.test.utils import override_settings
from nautobot.dcim.models import Platform
from nautobot.utilities.testing import TestCase

from nautobot_ssot_aristacv.signals import post_migrate_create_platform

settings = {
    "platform_name": "Something else"
}


class TestSettings(TestCase):
    """Test that the settings work correctly."""

    @override_settings(PLUGINS_CONFIG={"nautobot_ssot_aristacv": settings})
    def test_platform_name(self):
        """Verify that the 'platform_name' settings is used correctly."""
        # Make sure the signal callback runs
        post_migrate_create_platform()

        # Make sure the platform exists
        try:
            Platform.objects.get(name=settings["platform_name"])
        except Platform.DoesNotExist:
            self.fail(f"Platform with configured name {settings['platform_name']} was not created.")
