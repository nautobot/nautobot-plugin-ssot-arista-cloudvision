"""Unit tests for the Cloudvision DiffSync adapter class."""
import uuid
from unittest.mock import MagicMock, patch
from django.contrib.contenttypes.models import ContentType

from nautobot.extras.models import Job, JobResult
from nautobot.utilities.testing import TransactionTestCase
from nautobot_ssot_aristacv.diffsync.adapters.cloudvision import CloudvisionAdapter
from nautobot_ssot_aristacv.jobs import CloudVisionDataSource
from nautobot_ssot_aristacv.tests.fixtures import fixtures


class CloudvisionAdapterTestCase(TransactionTestCase):
    """Test the CloudvisionAdapter class."""

    databases = ("default", "job_logs")

    def setUp(self):
        """Method to initialize test case."""
        self.client = MagicMock()
        self.client.comm_channel = MagicMock()

        self.cloudvision = MagicMock()
        self.cloudvision.get_devices = MagicMock()
        self.cloudvision.get_devices.return_value = fixtures.DEVICE_FIXTURE
        self.cloudvision.get_tags_by_type = MagicMock()
        self.cloudvision.get_tags_by_type.return_value = []
        self.cloudvision.get_device_type = MagicMock()
        self.cloudvision.get_device_type.return_value = "fixedSystem"
        self.cloudvision.get_interfaces_fixed = MagicMock()
        self.cloudvision.get_interfaces_fixed.return_value = fixtures.INTERFACE_FIXTURE
        self.cloudvision.get_interface_mode = MagicMock()
        self.cloudvision.get_interface_mode.return_value = "access"
        self.cloudvision.get_interface_transceiver = MagicMock()
        self.cloudvision.get_interface_transceiver.return_value = "1000BASE-T"

        self.job = CloudVisionDataSource()
        self.job.job_result = JobResult.objects.create(
            name=self.job.class_path, obj_type=ContentType.objects.get_for_model(Job), user=None, job_id=uuid.uuid4()
        )
        self.cvp = CloudvisionAdapter(job=self.job, conn=self.client)

    def test_load_devices(self):
        """Test the load_devices() adapter method."""
        with patch("nautobot_ssot_aristacv.utils.cloudvision.get_devices", self.cloudvision.get_devices):
            with patch("nautobot_ssot_aristacv.utils.cloudvision.get_device_type", self.cloudvision.get_device_type):
                with patch(
                    "nautobot_ssot_aristacv.utils.cloudvision.get_interfaces_fixed",
                    self.cloudvision.get_interfaces_fixed,
                ):
                    self.cvp.load_devices()
        self.assertEqual(
            {dev["hostname"] for dev in fixtures.DEVICE_FIXTURE},
            {dev.get_unique_id() for dev in self.cvp.get_all("device")},
        )

    def test_load_interfaces(self):
        """Test the load_interfaces() adapter method."""
        mock_device = MagicMock()
        mock_device.name = "mock_device"
        mock_device.serial = MagicMock()
        mock_device.serial.return_value = "JPE12345678"
        mock_device.device_model = MagicMock()
        mock_device.device_model.return_value = "DCS-7280CR2-60"

        with patch("nautobot_ssot_aristacv.utils.cloudvision.get_device_type", self.cloudvision.get_device_type):
            with patch(
                "nautobot_ssot_aristacv.utils.cloudvision.get_interfaces_fixed", self.cloudvision.get_interfaces_fixed
            ):
                with patch(
                    "nautobot_ssot_aristacv.utils.cloudvision.get_interface_mode", self.cloudvision.get_interface_mode
                ):
                    with patch(
                        "nautobot_ssot_aristacv.utils.cloudvision.get_interface_transceiver",
                        self.cloudvision.get_interface_transceiver,
                    ):
                        self.cvp.load_interfaces(mock_device)
        self.assertEqual(
            {f"{port['interface']}__mock_device" for port in fixtures.INTERFACE_FIXTURE},
            {port.get_unique_id() for port in self.cvp.get_all("port")},
        )
