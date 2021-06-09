"""Diffsync models for Nautobot <-> CloudVision sync."""

from diffsync import DiffSyncModel
from typing import List

import aristacv_sync.diffsync.cvutils as cvutils


class Device(DiffSyncModel):
    """Device Model"""

    _modelname = "device"
    _identifiers = ("name",)
    _attributes = ()
    _children = {"tag": "tags"}

    name: str
    device_id: str
    tags: List = list()


class UserTag(DiffSyncModel):
    """Tag model"""

    _modelname = "tag"
    _identifiers = ("name", "value", "device_name")
    _shortname = ("name",)
    _attributes = ()

    name: str
    device_name: str
    value: str

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Apply user tag to a device in CloudVision."""
        device_obj = diffsync.get(Device, ids["device_name"])
        cvutils.create_tag(ids["name"], ids["value"])
        cvutils.assign_tag_to_device(device_obj.device_id, ids["name"], ids["value"])
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        ## TODO add your own logic here to update the device on the remote system
        # Call the super().update() method to update the in-memory DiffSyncModel instance
        return super().update(attrs)

    def delete(self):
        """Delete user tag applied to device in CloudVision."""

        # Call the super().delete() method to remove the DiffSyncModel instance from its parent DiffSync adapter
        super().delete()
        return self