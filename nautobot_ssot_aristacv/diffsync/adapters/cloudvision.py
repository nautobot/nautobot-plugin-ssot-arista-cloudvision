"""DiffSync adapter for Arista CloudVision."""
from diffsync import DiffSync
from django.forms import ValidationError
import arista.tag.v1 as TAG
from diffsync.exceptions import ObjectAlreadyExists
import distutils

from nautobot_ssot_aristacv.diffsync.models.cloudvision import CloudvisionDevice, CloudvisionCustomField
from nautobot_ssot_aristacv.utils import cloudvision


class CloudvisionAdapter(DiffSync):
    """DiffSync adapter implementation for CloudVision user-defined device tags."""

    device = CloudvisionDevice
    cf = CloudvisionCustomField

    top_level = ["device"]

    def __init__(self, *args, job=None, conn: cloudvision.CloudvisionApi, **kwargs):
        """Initialize the CloudVision DiffSync adapter."""
        super().__init__(*args, **kwargs)
        self.job = job
        self.conn = conn

    def load(self):
        """Load tag data from CloudVision."""
        devices = cloudvision.get_devices(client=self.conn.comm_channel)
        system_tags = cloudvision.get_tags_by_type(TAG.models.CREATOR_TYPE_SYSTEM)

        for dev in devices:
            new_device = None
            if dev["hostname"] != "":
                if self.job.kwargs.get("debug"):
                    self.job.log_debug(message=f"Device being loaded: {dev}")
                new_device = self.device(
                    name=dev["hostname"], serial=dev["device_id"], device_model=dev["model"], uuid=None
                )
                try:
                    self.add(new_device)
                except ValidationError as err:
                    self.job.log_warning(message=f"Unable to load Device {dev['hostname']}. {err}")
                    continue
                except ObjectAlreadyExists as err:
                    self.job.log_warning(
                        message=f"Duplicate device {dev['hostname']} {dev['device_id']} found and ignored."
                    )
            else:
                self.job.log_warning(message=f"Device {dev} is missing hostname so won't be imported.")
                continue

            dev_tags = [
                tag
                for tag in cloudvision.get_device_tags(client=self.conn.comm_channel, device_id=dev["device_id"])
                if tag in system_tags
            ]

            # Check if topology_type tag exists
            list_of_tag_names = [value["label"] for value in dev_tags]
            if "topology_type" not in list_of_tag_names:
                dev_tags.append({"label": "topology_type", "value": "-"})

            for tag in dev_tags:
                if tag["label"] in ["hostname", "serialnumber", "Container"]:
                    continue
                if tag["label"] == "mpls" or tag["label"] == "ztp":
                    tag["value"] = bool(distutils.util.strtobool(tag["value"]))

                new_cf = self.cf(name=f"arista_{tag['label']}", value=tag["value"], device_name=dev["hostname"])
                try:
                    self.add(new_cf)
                    if new_device:
                        new_device.add_child(new_cf)
                except ObjectAlreadyExists:
                    self.job.log_warning(
                        message=f"Duplicate object encountered for {tag['label']} on device {dev['hostname']}"
                    )
