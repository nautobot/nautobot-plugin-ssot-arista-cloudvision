"""Diffsync models for Nautobot <-> CloudVision sync."""
from diffsync import DiffSyncModel
from django.core.exceptions import ValidationError
from django.conf import settings
from nautobot.dcim.models import Device as NautobotDevice
from nautobot.dcim.models import Platform as NautobotPlatform
from typing import List, Optional
import nautobot_ssot_aristacv.diffsync.nbutils as nbutils
import nautobot_ssot_aristacv.diffsync.cvutils as cvutils
import distutils


DEFAULT_SITE = "cloudvision_imported"
DEFAULT_DEVICE_ROLE = "network"
DEFAULT_DEVICE_ROLE_COLOR = "ff0000"
DEFAULT_DEVICE_STATUS = "cloudvision_imported"
DEFAULT_DEVICE_STATUS_COLOR = "ff0000"
DEFAULT_DELETE_DEVICES_ON_SYNC = False
APPLY_IMPORT_TAG = False
MISSING_CUSTOM_FIELDS = []


class Device(DiffSyncModel):
    """Device Model."""

    _modelname = "device"
    _identifiers = ("name",)
    _shortname = ()
    _attributes = ()
    _children = {"cf": "cfs"}

    name: str
    cfs: List = list()
    device_model: Optional[str]

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create device object in Nautobot."""
        configs = settings.PLUGINS_CONFIG.get("nautobot_ssot_aristacv", {})
        default_site_object = nbutils.verify_site(configs.get("from_cloudvision_default_site", DEFAULT_SITE))

        cvutils.connect()
        device_dict = next((device for device in cvutils.get_devices() if device["hostname"] == ids["name"]), {})
        device_type_cv = device_dict.get("model")

        device_type_object = nbutils.verify_device_type_object(device_type_cv)
        device_role_object = nbutils.verify_device_role_object(
            configs.get("from_cloudvision_default_device_role", DEFAULT_DEVICE_ROLE),
            configs.get("from_cloudvision_default_device_role_color", DEFAULT_DEVICE_ROLE_COLOR),
        )

        device_status = nbutils.verify_device_status(
            configs.get("from_cloudvision_default_device_status", DEFAULT_DEVICE_STATUS),
            configs.get("from_cloudvision_default_device_status_color", DEFAULT_DEVICE_STATUS_COLOR),
        )

        new_device = NautobotDevice(
            status=device_status,
            device_type=device_type_object,
            device_role=device_role_object,
            site=default_site_object,
            name=ids["name"],
        )

        new_device = nbutils.assign_arista_cf(new_device)

        new_device.validated_save()

        if configs.get("apply_import_tag", APPLY_IMPORT_TAG):
            import_tag = nbutils.verify_import_tag()
            new_device.tags.add(import_tag)
            new_device.validated_save()

        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, diffsync, attrs):
        """Update device object in Nautobot."""
        return super().update(attrs, diffsync)

    def delete(self):
        """Delete device object in Nautobot."""
        configs = settings.PLUGINS_CONFIG.get("nautobot_ssot_aristacv", {})
        if configs.get("delete_devices_on_sync", DEFAULT_DELETE_DEVICES_ON_SYNC):
            self.diffsync.job.log_warning(message=f"Device {self.name} will be deleted per plugin settings.")
            device = NautobotDevice.objects.get(name=self.name)
            device.delete()
            super().delete()
        return self

    def ensure_default_cf(obj, model):
        """Update objects's default custom fields."""
        for cf in CustomField.objects.get_for_model(model):
            if (cf.default is not None) and (cf.name not in obj.cf):
                obj.cf[cf.name] = cf.default


class CustomField(DiffSyncModel):
    """Custom Field model."""

    _modelname = "cf"
    _identifiers = ("name", "device_name")
    _shortname = ()
    _attributes = ("value",)

    name: str
    value: str
    device_name: str

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Custom Field in Nautobot."""
        if ids["name"] == "arista_model":
            try:
                # Try to create new platform
                new_platform = NautobotPlatform(name=attrs["value"], slug=attrs["value"].lower())
                new_platform.validated_save()
                # Assign new platform to device.
                device = NautobotDevice.objects.get(name=ids["device_name"])
                device.platform = new_platform
                device.validated_save()
                return super().create(ids=ids, diffsync=diffsync, attrs=attrs)
            except ValidationError:
                # Assign existing platform to device.
                existing_platform = NautobotPlatform.objects.get(name=attrs["value"])
                device = NautobotDevice.objects.get(name=ids["device_name"])
                device.platform = existing_platform
                device.validated_save()
                return super().create(ids=ids, diffsync=diffsync, attrs=attrs)
        try:
            attrs["value"] = bool(distutils.util.strtobool(attrs["value"]))
        except ValueError:
            # value isn't convertable to bool so continue
            pass
        device = NautobotDevice.objects.get(name=ids["device_name"])
        try:
            device.custom_field_data.update({ids["name"]: attrs["value"]})
            device.validated_save()
        except ValidationError:
            if ids["name"] not in MISSING_CUSTOM_FIELDS:
                diffsync.job.log_warning(
                    message=f"Custom field {ids['name']} is not defined. You can create the custom field in the Admin UI."
                )
            MISSING_CUSTOM_FIELDS.append(ids["name"])

        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        """Update Custom Field in Nautobot."""
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
            except ValidationError:
                # Assign existing platform to device.
                existing_platform = NautobotPlatform.objects.get(name=attrs["value"])
                device = NautobotDevice.objects.get(name=self.device_name)
                device.platform = existing_platform
                device.validated_save()
                return super().update(attrs)
        try:
            attrs["value"] = bool(distutils.util.strtobool(attrs["value"]))
        except ValueError:
            # value isn't convertable to bool so continue
            pass
        device = NautobotDevice.objects.get(name=self.device_name)
        device.custom_field_data.update({self.name: attrs["value"]})
        device.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete Custom Field in Nautobot."""
        try:
            device = NautobotDevice.objects.get(name=self.device_name)
            if self.name == "arista_model":
                device.platform = None
            else:
                device.custom_field_data.update({self.name: None})
            device.validated_save()
            super().delete()
            return self
        except NautobotDevice.DoesNotExist:
            # Do not need to delete customfield if the device does not exist.
            return self
