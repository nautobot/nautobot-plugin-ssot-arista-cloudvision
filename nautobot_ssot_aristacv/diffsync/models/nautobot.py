"""Nautobot DiffSync models for AristaCV SSoT."""
from django.core.exceptions import ValidationError
from django.conf import settings
from nautobot.dcim.models import Device as OrmDevice
from nautobot.dcim.models import Platform as OrmPlatform
from nautobot.extras.models import CustomField as OrmCustomField
from nautobot_ssot_aristacv.diffsync.models.base import Device, CustomField
from nautobot_ssot_aristacv.utils import nautobot, cloudvision
import distutils


DEFAULT_SITE = "cloudvision_imported"
DEFAULT_DEVICE_ROLE = "network"
DEFAULT_DEVICE_ROLE_COLOR = "ff0000"
DEFAULT_DEVICE_STATUS = "cloudvision_imported"
DEFAULT_DEVICE_STATUS_COLOR = "ff0000"
DEFAULT_DELETE_DEVICES_ON_SYNC = False
APPLY_IMPORT_TAG = False
MISSING_CUSTOM_FIELDS = []


class NautobotDevice(Device):
    """Nautobot Device Model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create device object in Nautobot."""
        configs = settings.PLUGINS_CONFIG.get("nautobot_ssot_aristacv", {})
        default_site_object = nautobot.verify_site(configs.get("from_cloudvision_default_site", DEFAULT_SITE))

        cloudvision.connect()
        device_dict = next((device for device in cloudvision.get_devices() if device["hostname"] == ids["name"]), {})
        device_type_cv = device_dict.get("model")

        device_type_object = nautobot.verify_device_type_object(device_type_cv)
        device_role_object = nautobot.verify_device_role_object(
            configs.get("from_cloudvision_default_device_role", DEFAULT_DEVICE_ROLE),
            configs.get("from_cloudvision_default_device_role_color", DEFAULT_DEVICE_ROLE_COLOR),
        )

        device_status = nautobot.verify_device_status(
            configs.get("from_cloudvision_default_device_status", DEFAULT_DEVICE_STATUS),
            configs.get("from_cloudvision_default_device_status_color", DEFAULT_DEVICE_STATUS_COLOR),
        )

        new_device = OrmDevice(
            status=device_status,
            device_type=device_type_object,
            device_role=device_role_object,
            site=default_site_object,
            name=ids["name"],
        )

        new_device = nautobot.assign_arista_cf(new_device)

        new_device.validated_save()

        if configs.get("apply_import_tag", APPLY_IMPORT_TAG):
            import_tag = nautobot.verify_import_tag()
            new_device.tags.add(import_tag)
            new_device.validated_save()

        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        """Update device object in Nautobot."""
        return super().update(attrs)

    def delete(self):
        """Delete device object in Nautobot."""
        configs = settings.PLUGINS_CONFIG.get("nautobot_ssot_aristacv", {})
        if configs.get("delete_devices_on_sync", DEFAULT_DELETE_DEVICES_ON_SYNC):
            self.diffsync.job.log_warning(message=f"Device {self.name} will be deleted per plugin settings.")
            device = OrmDevice.objects.get(name=self.name)
            device.delete()
            super().delete()
        return self

    def ensure_default_cf(obj, model):
        """Update objects's default custom fields."""
        for cf in OrmCustomField.objects.get_for_model(model):
            if (cf.default is not None) and (cf.name not in obj.cf):
                obj.cf[cf.name] = cf.default


class NautobotCustomField(CustomField):
    """Nautobot CustomField model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Custom Field in Nautobot."""
        if ids["name"] == "arista_model":
            try:
                # Try to create new platform
                new_platform = OrmPlatform(name=attrs["value"], slug=attrs["value"].lower())
                new_platform.validated_save()
                # Assign new platform to device.
                device = OrmDevice.objects.get(name=ids["device_name"])
                device.platform = new_platform
                device.validated_save()
                return super().create(ids=ids, diffsync=diffsync, attrs=attrs)
            except ValidationError:
                # Assign existing platform to device.
                existing_platform = OrmPlatform.objects.get(name=attrs["value"])
                device = OrmDevice.objects.get(name=ids["device_name"])
                device.platform = existing_platform
                device.validated_save()
                return super().create(ids=ids, diffsync=diffsync, attrs=attrs)
        try:
            attrs["value"] = bool(distutils.util.strtobool(attrs["value"]))
        except ValueError:
            # value isn't convertable to bool so continue
            pass
        device = OrmDevice.objects.get(name=ids["device_name"])
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
                new_platform = OrmPlatform(name=attrs["value"], slug=attrs["value"].lower())
                new_platform.validated_save()
                # Assign new platform to device.
                device = OrmDevice.objects.get(name=self.device_name)
                device.platform = new_platform
                device.validated_save()
                return super().update(attrs)
            except ValidationError:
                # Assign existing platform to device.
                existing_platform = OrmPlatform.objects.get(name=attrs["value"])
                device = OrmDevice.objects.get(name=self.device_name)
                device.platform = existing_platform
                device.validated_save()
                return super().update(attrs)
        try:
            attrs["value"] = bool(distutils.util.strtobool(attrs["value"]))
        except ValueError:
            # value isn't convertable to bool so continue
            pass
        device = OrmDevice.objects.get(name=self.device_name)
        device.custom_field_data.update({self.name: attrs["value"]})
        device.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete Custom Field in Nautobot."""
        try:
            device = OrmDevice.objects.get(name=self.device_name)
            if self.name == "arista_model":
                device.platform = None
            else:
                device.custom_field_data.update({self.name: None})
            device.validated_save()
            super().delete()
            return self
        except OrmDevice.DoesNotExist:
            # Do not need to delete customfield if the device does not exist.
            return self
