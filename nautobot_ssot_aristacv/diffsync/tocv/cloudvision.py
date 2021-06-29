"""DiffSync adapter for Arista CloudVision."""
from diffsync import DiffSync

import nautobot_ssot_aristacv.diffsync.cvutils as cvutils

from .models import UserTag


class CloudVision(DiffSync):
    """DiffSync adapter implementation for CloudVision user-defined device tags."""

    tag = UserTag

    top_level = ["tag"]

    type = "CloudVision"

    def __init__(self, *args, job=None, **kwargs):
        """Initialize the CloudVision DiffSync adapter."""
        super().__init__(*args, **kwargs)
        self.job = job

    def load(self):
        """Load tag data from CloudVision."""
        user_tags = cvutils.get_tags_by_type()
        for tag in user_tags:
            self.tag = UserTag(name=tag["label"], value=tag["value"])
            self.add(self.tag)

        devices = cvutils.get_devices()
        for dev in devices:
            hostname = dev["hostname"]
            # Filter device tags to user-defined tags only
            dev_tags = [tag for tag in cvutils.get_device_tags(device_id=dev["device_id"]) if tag in user_tags]
            for tag in dev_tags:
                cur_tag = self.get(UserTag, f"{tag['label']}__{tag['value']}")
                cur_tag.devices.append(hostname)

        # Sort device list of all tags for diffsync
        for tag in self.get_all(UserTag):
            tag.devices = sorted(tag.devices)
