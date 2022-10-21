"""Tests of Cloudvision utility methods."""
from django.conf import settings
from nautobot.utilities.testing import TestCase
from nautobot_ssot_aristacv.utils import nautobot

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG["nautobot_ssot_aristacv"]


class TestNautobotUtils(TestCase):
    """Test Nautobot utility methods."""

    databases = ("default", "job_logs")

    def test_parse_hostname(self):
        """Test the parse_hostname method."""
        original = PLUGIN_SETTINGS["hostname_patterns"]
        PLUGIN_SETTINGS["hostname_patterns"] = [r"(?P<site>\w{2,3}\d+)-(?P<role>\w+)-\d+"]
        host = "ams01-leaf-01"
        results = nautobot.parse_hostname(host)
        expected = ("ams01", "leaf")
        self.assertEqual(results, expected)
        PLUGIN_SETTINGS["hostname_patterns"] = original

    def test_get_site_from_map_success(self):
        """Test the get_site_from_map method with response."""
        original = PLUGIN_SETTINGS["site_mapping"]
        PLUGIN_SETTINGS["site_mapping"] = {"ams01": "Amsterdam"}
        results = nautobot.get_site_from_map("ams01")
        expected = "Amsterdam"
        self.assertEqual(results, expected)
        PLUGIN_SETTINGS["site_mapping"] = original

    def test_get_site_from_map_fail(self):
        """Test the get_site_from_map method with failed response."""
        original = PLUGIN_SETTINGS["site_mapping"]
        PLUGIN_SETTINGS["site_mapping"] = {"ams01": "Amsterdam"}
        results = nautobot.get_site_from_map("dc01")
        expected = None
        self.assertEqual(results, expected)
        PLUGIN_SETTINGS["site_mapping"] = original

    def test_get_role_from_map_success(self):
        """Test the get_role_from_map method with response."""
        original = PLUGIN_SETTINGS["role_mapping"]
        PLUGIN_SETTINGS["role_mapping"] = {"edge": "Edge Router"}
        results = nautobot.get_role_from_map("edge")
        expected = "Edge Router"
        self.assertEqual(results, expected)
        PLUGIN_SETTINGS["role_mapping"] = original

    def test_get_role_from_map_fail(self):
        """Test the get_role_from_map method with failed response."""
        original = PLUGIN_SETTINGS["role_mapping"]
        PLUGIN_SETTINGS["role_mapping"] = {"edge": "Edge Router"}
        results = nautobot.get_role_from_map("rtr")
        expected = None
        self.assertEqual(results, expected)
        PLUGIN_SETTINGS["role_mapping"] = original
