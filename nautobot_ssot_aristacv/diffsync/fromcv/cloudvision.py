"""DiffSync adapter for Arista CloudVision."""
from diffsync import DiffSync
import arista.tag.v1 as TAG
from diffsync.exceptions import ObjectAlreadyExists
import nautobot_ssot_aristacv.diffsync.cvutils as cvutils
import distutils

from .models import Device, CustomField


class CloudVision(DiffSync):
    """DiffSync adapter implementation for CloudVision user-defined device tags."""

    device = Device
    cf = CustomField

    top_level = ["device"]

    def __init__(self, *args, job=None, **kwargs):
        """Initialize the CloudVision DiffSync adapter."""
        super().__init__(*args, **kwargs)
        self.job = job

    def load(self):
        """Load tag data from CloudVision."""
        devices = cvutils.get_devices()
        system_tags = cvutils.get_tags_by_type(TAG.models.CREATOR_TYPE_SYSTEM)

        for dev in devices:
            self.device = Device(name=dev["hostname"], device_id=dev["device_id"], device_model=dev["model"])
            self.add(self.device)

            dev_tags = [tag for tag in cvutils.get_device_tags(device_id=dev["device_id"]) if tag in system_tags]

            # Check if topology_type tag exists
            list_of_tag_names = [value["label"] for value in dev_tags]
            if "topology_type" not in list_of_tag_names:
                dev_tags.append({"label": "topology_type", "value": "-"})

            for tag in dev_tags:
                if tag["label"] in ["hostname", "serialnumber", "Container"]:
                    continue
                if tag["label"] == "mpls" or tag["label"] == "ztp":
                    tag["value"] = bool(distutils.util.strtobool(tag["value"]))

                self.cf = CustomField(name=f"arista_{tag['label']}", value=tag["value"], device_name=dev["hostname"])
                try:
                    self.add(self.cf)
                    self.device.add_child(self.cf)
                except ObjectAlreadyExists:
                    self.job.log_warning(
                        message=f"Duplicate object encountered for {tag['label']} on device {self.device.name}"
                    )
