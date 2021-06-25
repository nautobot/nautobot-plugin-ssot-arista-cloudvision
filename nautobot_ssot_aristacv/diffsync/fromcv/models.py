"""Diffsync models for Nautobot <-> CloudVision sync."""
from diffsync import DiffSyncModel
from django.core.exceptions import ValidationError
from nautobot.dcim.models import Device as NautobotDevice
from nautobot.dcim.models import Platform as NautobotPlatform
from typing import List
import distutils

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
        # Call the super().create() method to create the in-memory DiffSyncModel instance
        #new_device = NautobotDevice(status = "", device_type = "", device_role="", site="", name=ids["name"])
        #new_device.validated_save()
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
        if self.name == "arista_model":
            try:
                # Try to create new platform
                new_platform = NautobotPlatform(name=attrs["value"], slug=attrs["value"].lower())
                new_platform.validated_save()
                # Assign new platform to device.
                device = NautobotDevice.objects.get(name=self.device_name)
                device.platform = new_platform
                device.validated_save()
                return super().update(attrs)
            except ValidationError as e:
                # Assign existing platform to device.
                existing_platform = NautobotPlatform.objects.get(name=attrs["value"])
                device = NautobotDevice.objects.get(name=self.device_name)
                device.platform = existing_platform
                device.validated_save()
                return super().update(attrs)
        try:
            attrs["value"] = bool(distutils.util.strtobool(attrs["value"]))
        except ValueError as e:
            # value isn't convertable to bool so continue
            pass
        device = NautobotDevice.objects.get(name=self.device_name)
        device.custom_field_data.update({self.name: attrs["value"]})
        device.validated_save()
        return super().update(attrs)


    def delete(self):
        # Call the super().delete() method to remove the DiffSyncModel instance from its parent DiffSync adapter
        print(self.name)
        device = NautobotDevice.objects.get(name=self.device_name)
        device.custom_field_data.update({self.name: "-"})
        device.validated_save()
        super().delete()
        return self
