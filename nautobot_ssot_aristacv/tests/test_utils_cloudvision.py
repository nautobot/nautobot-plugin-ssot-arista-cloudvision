"""Tests of Cloudvision utility methods."""
import json

from unittest.mock import MagicMock, patch
from parameterized import parameterized

from nautobot.utilities.testing import TestCase
from nautobot_ssot_aristacv.utils import cloudvision


def load_json(path):
    """Load a json file."""
    with open(path, encoding="utf-8") as file:
        return json.loads(file.read())


DEVICE_FIXTURE = load_json("./nautobot_ssot_aristacv/tests/fixtures/get_devices_response.json")

class TestCloudvisionUtils(TestCase):
    """Test Cloudvision utility methods."""

    databases = ("default", "job_logs")

    def setUp(self):
        """Setup mock Cloudvision client."""
        self.client = MagicMock()

    def test_get_devices(self):
        """Test get_devices function."""
        device1 = MagicMock()
        device1.value.key.device_id.value = "JPE12345678"
        device1.value.hostname.value = "ams01-edge-01.ntc.com"
        device1.value.fqdn.value = "ams01-edge-01.ntc.com"
        device1.value.software_version.value = "4.26.5M"
        device1.value.model_name.value = "DCS-7280CR2-60"
        device1.value.system_mac_address.value = "12:34:56:78:ab:cd"

        device2 = MagicMock()
        device2.value.key.device_id.value = "JPE12345679"
        device2.value.hostname.value = "ams01-edge-02.ntc.com"
        device2.value.fqdn.value = "ams01-edge-02.ntc.com"
        device2.value.software_version.value = "4.26.5M"
        device2.value.model_name.value = "DCS-7280CR2-60"
        device2.value.system_mac_address.value = "12:34:56:78:ab:ce"

        device_list = [device1, device2]

        device_svc_stub = MagicMock()
        device_svc_stub.DeviceServiceStub.return_value.GetAll.return_value = device_list

        with patch("nautobot_ssot_aristacv.utils.cloudvision.services", device_svc_stub):
            results = cloudvision.get_devices(client=self.client)
        expected = DEVICE_FIXTURE
        self.assertEqual(results, expected)
