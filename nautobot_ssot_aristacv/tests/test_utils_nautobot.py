"""Tests of Cloudvision utility methods."""
from django.test import override_settings
from nautobot.utilities.testing import TestCase
from nautobot_ssot_aristacv.utils import nautobot


class TestNautobotUtils(TestCase):
    """Test Nautobot utility methods."""

    databases = ("default", "job_logs")

    @override_settings(
        PLUGINS_CONFIG={"nautobot_ssot_aristacv": {"hostname_patterns": [r"(?P<site>\w{2,3}\d+)-(?P<role>\w+)-\d+"]}}
    )
    def test_parse_hostname(self):
        """Test the parse_hostname method."""
        host = "ams01-leaf-01"
        results = nautobot.parse_hostname(host)
        expected = ("ams01", "leaf")
        self.assertEqual(results, expected)

    @override_settings(PLUGINS_CONFIG={"nautobot_ssot_aristacv": {"site_mapping": {"ams01": "Amsterdam"}}})
    def test_get_site_from_map_success(self):
        """Test the get_site_from_map method with response."""
        results = nautobot.get_site_from_map("ams01")
        expected = "Amsterdam"
        self.assertEqual(results, expected)

    @override_settings(PLUGINS_CONFIG={"nautobot_ssot_aristacv": {"site_mapping": {}}})
    def test_get_site_from_map_fail(self):
        """Test the get_site_from_map method with failed response."""
        results = nautobot.get_site_from_map("dc01")
        expected = None
        self.assertEqual(results, expected)

    @override_settings(PLUGINS_CONFIG={"nautobot_ssot_aristacv": {"role_mapping": {"edge": "Edge Router"}}})
    def test_get_role_from_map_success(self):
        """Test the get_role_from_map method with response."""
        results = nautobot.get_role_from_map("edge")
        expected = "Edge Router"
        self.assertEqual(results, expected)

    @override_settings(PLUGINS_CONFIG={"nautobot_ssot_aristacv": {"role_mapping": {}}})
    def test_get_role_from_map_fail(self):
        """Test the get_role_from_map method with failed response."""
        results = nautobot.get_role_from_map("rtr")
        expected = None
        self.assertEqual(results, expected)
