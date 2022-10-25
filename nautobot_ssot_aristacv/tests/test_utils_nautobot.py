"""Tests of Cloudvision utility methods."""
from django.test import override_settings
from nautobot.dcim.models import DeviceRole, DeviceType, Manufacturer, Site
from nautobot.extras.models import Tag
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

    def test_verify_device_type_object_success(self):
        """Test the verify_device_type_object for existing DeviceType."""
        new_dt, _ = DeviceType.objects.get_or_create(
            model="DCS-7150S-24", slug="dcs-7150s-24", manufacturer=Manufacturer.objects.get(slug="arista")
        )
        result = nautobot.verify_device_type_object(device_type="DCS-7150S-24")
        self.assertEqual(result, new_dt)

    def test_verify_device_type_object_fail(self):
        """Test the verify_device_type_object for non-existing DeviceType."""
        result = nautobot.verify_device_type_object(device_type="DCS-7150S-24")
        self.assertEqual(result.model, "DCS-7150S-24")
        self.assertEqual(result.slug, "dcs-7150s-24")
        self.assertTrue(isinstance(result, DeviceType))

    def test_verify_device_role_object_success(self):
        """Test the verify_device_role_object method for existing DeviceRole."""
        new_dr, _ = DeviceRole.objects.get_or_create(name="Edge Router", slug="edge-router")
        result = nautobot.verify_device_role_object(role_name="Edge Router", role_color="ff0000")
        self.assertEqual(result, new_dr)

    def test_verify_device_role_object_fail(self):
        """Test the verify_device_role_object method for non-existing DeviceRole."""
        result = nautobot.verify_device_role_object(role_name="Distro Switch", role_color="ff0000")
        self.assertEqual(result.name, "Distro Switch")
        self.assertEqual(result.slug, "distro-switch")
        self.assertEqual(result.color, "ff0000")

    def test_verify_import_tag_success(self):
        """Test the verify_import_tag method for existing Tag."""
        new_tag, _ = Tag.objects.get_or_create(name="cloudvision_imported", slug="cloudvision_imported")
        result = nautobot.verify_import_tag()
        self.assertEqual(result, new_tag)

    def test_verify_import_tag_fail(self):
        """Test the verify_import_tag method for non-existing Tag."""
        result = nautobot.verify_import_tag()
        self.assertEqual(result.name, "cloudvision_imported")
        self.assertEqual(result.slug, "cloudvision_imported")

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
