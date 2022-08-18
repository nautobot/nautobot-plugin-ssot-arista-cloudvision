"""DiffSync adapter for Arista CloudVision."""
from diffsync import DiffSync
from django.forms import ValidationError
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
            new_device = None
            if dev["hostname"] != "":
                if self.job.kwargs.get("debug"):
                    self.job.log_debug(message=f"Device being loaded: {dev}")
                new_device = self.device(name=dev["hostname"], device_id=dev["device_id"], device_model=dev["model"])
                try:
                    self.add(new_device)
                except ValidationError as err:
                    self.job.log_warning(message=f"Unable to load Device {dev['hostname']}. {err}")
                    continue
            else:
                self.job.log_warning(message=f"Device {dev} is missing hostname so won't be imported.")
                continue

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

                new_cf = self.cf(name=f"arista_{tag['label']}", value=tag["value"], device_name=dev["hostname"])
                try:
                    self.add(new_cf)
                    if new_device:
                        new_device.add_child(new_cf)
                except ObjectAlreadyExists:
                    self.job.log_warning(
                        message=f"Duplicate object encountered for {tag['label']} on device {dev['hostname']}"
                    )
