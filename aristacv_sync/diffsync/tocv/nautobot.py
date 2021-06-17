"""DiffSync adapter for Nautobot."""
from nautobot.dcim.models import Device
from nautobot.extras.models.tags import Tag
from diffsync import DiffSync

from .models import UserTag


class Nautobot(DiffSync):
    """DiffSync adapter implementation for Nautobot user-defined tags."""

    tag = UserTag

    top_level = ["tag"]

    type = "Nautobot"

    def load(self):
        """Load device tag data from Nautobot and populate DiffSync models."""
        tags = Tag.objects.all()
        for cur_tag in tags:
            if ":" in cur_tag.name:
                label, value = cur_tag.name.split(":")
            else:
                label = cur_tag.name
                value = ""
            self.tag = UserTag(name=label, value=value)
            tagged_devices = Device.objects.filter(tags__name__exact=cur_tag.name)
            for dev in tagged_devices:
                self.tag.devices.append(dev.name)

            # Sort device list for diffsync
            self.tag.devices = sorted(self.tag.devices)
            self.add(self.tag)
