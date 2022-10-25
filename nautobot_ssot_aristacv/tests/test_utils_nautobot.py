"""Tests of Cloudvision utility methods."""
from django.test import override_settings
from nautobot.dcim.models import Site
from nautobot.utilities.testing import TestCase
from nautobot_ssot_aristacv.utils import nautobot


class TestNautobotUtils(TestCase):
    """Test Nautobot utility methods."""

    databases = ("default", "job_logs")

    def test_verify_site_success(self):
        """Test the verify_site method for existing Site."""
        test_site, _ = Site.objects.get_or_create(name="Test")
        result = nautobot.verify_site(site_name="Test")
        self.assertEqual(result, test_site)

    def test_verify_site_fail(self):
        """Test the verify_site method for non-existing Site."""
        result = nautobot.verify_site(site_name="Test2")
        self.assertEqual(result.name, "Test2")
        self.assertEqual(result.slug, "test2")
        self.assertTrue(isinstance(result, Site))

    @override_settings(
        PLUGINS_CONFIG={"nautobot_ssot_aristacv": {"hostname_patterns": [r"(?P<site>\w{2,3}\d+)-(?P<role>\w+)-\d+"]}}
    )
    def test_parse_hostname(self):
        """Test the parse_hostname method."""
        host = "ams01-leaf-01"
        results = nautobot.parse_hostname(host)
        expected = ("ams01", "leaf")
        self.assertEqual(results, expected)

    @override_settings(PLUGINS_CONFIG={"nautobot_ssot_aristacv": {"site_mappings": {"ams01": "Amsterdam"}}})
    def test_get_site_from_map_success(self):
        """Test the get_site_from_map method with response."""
        results = nautobot.get_site_from_map("ams01")
        expected = "Amsterdam"
        self.assertEqual(results, expected)

    @override_settings(PLUGINS_CONFIG={"nautobot_ssot_aristacv": {"site_mappings": {}}})
    def test_get_site_from_map_fail(self):
        """Test the get_site_from_map method with failed response."""
        results = nautobot.get_site_from_map("dc01")
        expected = None
        self.assertEqual(results, expected)

    @override_settings(PLUGINS_CONFIG={"nautobot_ssot_aristacv": {"role_mappings": {"edge": "Edge Router"}}})
    def test_get_role_from_map_success(self):
        """Test the get_role_from_map method with response."""
        results = nautobot.get_role_from_map("edge")
        expected = "Edge Router"
        self.assertEqual(results, expected)

    @override_settings(PLUGINS_CONFIG={"nautobot_ssot_aristacv": {"role_mappings": {}}})
    def test_get_role_from_map_fail(self):
        """Test the get_role_from_map method with failed response."""
        results = nautobot.get_role_from_map("rtr")
        expected = None
        self.assertEqual(results, expected)
