"""Tests of Cloudvision utility methods."""
from unittest.mock import MagicMock, patch
from parameterized import parameterized

from nautobot.utilities.testing import TestCase
from nautobot_ssot_aristacv.utils import cloudvision
from nautobot_ssot_aristacv.tests.fixtures import fixtures


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
        expected = fixtures.DEVICE_FIXTURE
        self.assertEqual(results, expected)

    def test_get_tags(self):
        """Test get_tags method."""

        mock_tag = MagicMock()
        mock_tag.value.key.label.value = "test"
        mock_tag.value.key.value.value = "test"
        mock_tag.value.creator_type = 1

        device_tag_stub = MagicMock()
        device_tag_stub.DeviceTagServiceStub.return_value.GetAll.return_value = [mock_tag]

        with patch("nautobot_ssot_aristacv.utils.cloudvision.tag_services", device_tag_stub):
            results = cloudvision.get_tags(client=self.client)
        expected = [{"label": "test", "value": "test", "creator_type": 1}]
        self.assertEqual(results, expected)

    def test_get_interfaces_fixed(self):
        """Test get_interfaces_fixed method."""
        mock_query = MagicMock()
        mock_query.dataset.type = "device"
        mock_query.dataset.name = "JPE12345678"
        mock_query.paths.path_elements = [
            "\304\005Sysdb",
            "\304\tinterface",
            "\304\006status",
            "\304\003eth",
            "\304\003phy",
            "\304\005slice",
            "\304\0011",
            "\304\nintfStatus",
            "\304\00\001",
        ]

        with patch("cloudvision.Connector.grpc_client.grpcClient.create_query", mock_query):
            self.client.get = MagicMock()
            self.client.get.return_value = fixtures.FIXED_INTF_QUERY
            results = cloudvision.get_interfaces_fixed(client=self.client, dId="JPE12345678")
        expected = fixtures.INTERFACE_FIXTURE
        self.assertEqual(results, expected)

    port_types = [
        ("built_in_gig", {"port_info": {}, "transceiver": "xcvr1000BaseT"}, "1000base-t"),
        ("build_in_10g_sr", {"port_info": {}, "transceiver": "xcvr10GBaseSr"}, "10gbase-x-xfp"),
        ("management_port", {"port_info": {"interface": "Management1"}, "transceiver": "Unknown"}, "1000base-t"),
        ("vlan_port", {"port_info": {"interface": "Vlan100"}, "transceiver": "Unknown"}, "virtual"),
        ("loopback_port", {"port_info": {"interface": "Loopback0"}, "transceiver": "Unknown"}, "virtual"),
        ("port_channel_port", {"port_info": {"interface": "Port-Channel10"}, "transceiver": "Unknown"}, "lag"),
        ("unknown_ethernet_port", {"port_info": {"interface": "Ethernet1"}, "transceiver": "Unknown"}, "other"),
    ]

    @parameterized.expand(port_types, skip_on_empty=True)
    def test_get_port_type(self, name, sent, received):  # pylint: disable=unused-argument
        """Test the get_port_type method."""
        self.assertEqual(
            cloudvision.get_port_type(port_info=sent["port_info"], transceiver=sent["transceiver"]), received
        )

    port_statuses = [
        ("active_port", {"link_status": "up", "oper_status": "up"}, "active"),
        ("planned_port", {"link_status": "down", "oper_status": "up"}, "planned"),
        ("maintenance_port", {"link_status": "down", "oper_status": "down"}, "maintenance"),
        ("decommissioning_port", {"link_status": "up", "oper_status": "down"}, "decommissioning"),
    ]

    @parameterized.expand(port_statuses, skip_on_empty=True)
    def test_get_interface_status(self, name, sent, received):  # pylint: disable=unused-argument
        """Test the get_interface_status method."""
        self.assertEqual(cloudvision.get_interface_status(port_info=sent), received)
