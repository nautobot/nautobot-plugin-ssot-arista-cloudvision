"""Diffsync models for Nautobot <-> CloudVision sync."""
from diffsync import DiffSyncModel
from nautobot.dcim.models import Device as NautobotDevice
from typing import List

class Device(DiffSyncModel):
    """Device Model"""

    _modelname = "device"
    _identifiers = ("name",)
    _shortname = ()
    _attributes = ()
    _children = {"cf": "cfs"}

    name: str
    cfs: List = list()

    @classmethod
    def create(cls, diffsync, ids, attrs):
        ## TODO add your own logic here to create the device on the remote system
        # Call the super().create() method to create the in-memory DiffSyncModel instance
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, diffsync, attrs):
        ## TODO add your own logic here to update the device on the remote system
        # Call the super().update() method to update the in-memory DiffSyncModel instance
        return super().update(attrs, diffsync)

    def delete(self):
        ## TODO add your own logic here to delete the device on the remote system
        # Call the super().delete() method to remove the DiffSyncModel instance from its parent DiffSync adapter
        super().delete()
        return self

class CustomField(DiffSyncModel):
    """Custom Field model"""

    _modelname = "cf"
    _identifiers = ("name", "device_name")
    _shortname = ()
    _attributes = ("value",)

    name: str
    value: str
    device_name: str

    @classmethod
    def create(cls, diffsync, ids, attrs):
        ## TODO add your own logic here to create the device on the remote system
        # Call the super().create() method to create the in-memory DiffSyncModel instance
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        # Call the super().update() method to update the in-memory DiffSyncModel instance
        if attrs["value"] == "false":
            attrs["value"] = False
        elif attrs["value"] == "true":
            attrs["value"] == True
        device = NautobotDevice.objects.get(name=self.device_name)
        device.custom_field_data.update({self.name: attrs["value"]})
        device.validated_save()
        return super().update(attrs)


    def delete(self):
        ## TODO add your own logic here to delete the device on the remote system
        # Call the super().delete() method to remove the DiffSyncModel instance from its parent DiffSync adapter
        super().delete()
        return self
