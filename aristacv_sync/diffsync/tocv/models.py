"""Diffsync models for Nautobot <-> CloudVision sync."""

from diffsync import DiffSyncModel
from typing import List

import aristacv_sync.diffsync.cvutils as cvutils


class UserTag(DiffSyncModel):
    """Tag model"""

    _modelname = "tag"
    _identifiers = ("name", "value")
    _attributes = ("devices",)

    name: str
    value: str
    devices: List = list()

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create a user tag in CloudVision."""
        cvutils.create_tag(ids["name"], ids["value"])
        # Create mapping from device_name to CloudVision device_id
        device_ids = {dev["hostname"]: dev["device_id"] for dev in cvutils.get_devices()}
        for device in attrs["devices"]:
            cvutils.assign_tag_to_device(device_ids[device], ids["name"], ids["value"])
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        remove = set(self.devices) - set(attrs["devices"])
        add = set(attrs["devices"]) - set(self.devices)
        # Create mapping from device_name to CloudVision device_id
        device_ids = {dev["hostname"]: dev["device_id"] for dev in cvutils.get_devices()}
        for device in remove:
            cvutils.remove_tag_from_device(device_ids[device], self.name, self.value)
        for device in add:
            cvutils.assign_tag_to_device(device_ids[device], self.name, self.value)
        # Call the super().update() method to update the in-memory DiffSyncModel instance
        return super().update(attrs)

    def delete(self):
        """Delete user tag applied to device in CloudVision."""
        device_ids = {dev["hostname"]: dev["device_id"] for dev in cvutils.get_devices()}
        for device in self.devices:
            cvutils.remove_tag_from_device(device_ids[device], self.name, self.value)
        cvutils.delete_tag(self.name, self.value)
        # Call the super().delete() method to remove the DiffSyncModel instance from its parent DiffSync adapter
        super().delete()
        return self
