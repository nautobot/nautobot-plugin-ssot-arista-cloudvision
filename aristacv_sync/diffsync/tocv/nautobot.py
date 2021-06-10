"""DiffSync adapter for Nautobot."""
from nautobot.dcim.models import Device as NautobotDevice
from nautobot.extras.models.tags import Tag
from diffsync import DiffSync

from .models import Device, UserTag


class Nautobot(DiffSync):
    """DiffSync adapter implementation for Nautobot user-defined tags."""

    device = Device
    tag = Tag

    top_level = ["device"]

    type = "Nautobot"

    nb = None

    def load(self):
        """Load device tag data from Nautobot and populate DiffSync models."""
        devices = NautobotDevice.objects.all()
        for dev in devices:
            self.device = Device(name=dev.name, device_id=dev.serial)
            self.add(self.device)
            dev_tags = dev.tags.all()
            for tag in dev_tags:
                if ":" in tag.name:
                    label, value = tag.name.split(":")
                else:
                    label = tag.name
                    value = ""
                self.tag = UserTag(name=label, device_name=dev.name, value=value)
                self.add(self.tag)
                self.device.add_child(self.tag)
