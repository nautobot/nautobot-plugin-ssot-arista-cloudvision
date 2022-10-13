"""Nautobot DiffSync models for AristaCV SSoT."""
from django.core.exceptions import ValidationError
from django.conf import settings
from nautobot.core.settings_funcs import is_truthy
from nautobot.dcim.models import Device as OrmDevice
from nautobot.dcim.models import Interface as OrmInterface
from nautobot.dcim.models import Platform as OrmPlatform
from nautobot.extras.models import Status as OrmStatus
from nautobot_ssot_aristacv.diffsync.models.base import Device, CustomField, Port
from nautobot_ssot_aristacv.utils import nautobot
import distutils


DEFAULT_SITE = "cloudvision_imported"
DEFAULT_DEVICE_ROLE = "network"
DEFAULT_DEVICE_ROLE_COLOR = "ff0000"
DEFAULT_DEVICE_STATUS = "cloudvision_imported"
DEFAULT_DEVICE_STATUS_COLOR = "ff0000"
DEFAULT_DELETE_DEVICES_ON_SYNC = False
APPLY_IMPORT_TAG = False
MISSING_CUSTOM_FIELDS = []
PLUGIN_SETTINGS = settings.PLUGINS_CONFIG["nautobot_ssot_aristacv"]


class NautobotDevice(Device):
    """Nautobot Device Model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create device object in Nautobot."""
        default_site_object = nautobot.verify_site(PLUGIN_SETTINGS.get("from_cloudvision_default_site", DEFAULT_SITE))

        device_type_cv = attrs["device_model"]

        device_type_object = nautobot.verify_device_type_object(device_type_cv)
        device_role_object = nautobot.verify_device_role_object(
            PLUGIN_SETTINGS.get("from_cloudvision_default_device_role", DEFAULT_DEVICE_ROLE),
            PLUGIN_SETTINGS.get("from_cloudvision_default_device_role_color", DEFAULT_DEVICE_ROLE_COLOR),
        )

        device_status = nautobot.verify_device_status(
            PLUGIN_SETTINGS.get("from_cloudvision_default_device_status", DEFAULT_DEVICE_STATUS),
            PLUGIN_SETTINGS.get("from_cloudvision_default_device_status_color", DEFAULT_DEVICE_STATUS_COLOR),
        )

        new_device = OrmDevice(
            status=device_status,
            device_type=device_type_object,
            device_role=device_role_object,
            site=default_site_object,
            name=ids["name"],
            serial=attrs["serial"] if attrs.get("serial") else "",
        )
        if PLUGIN_SETTINGS.get("apply_import_tag", APPLY_IMPORT_TAG):
            import_tag = nautobot.verify_import_tag()
            new_device.tags.add(import_tag)
        try:
            new_device.validated_save()
            return super().create(ids=ids, diffsync=diffsync, attrs=attrs)
        except ValidationError as err:
            diffsync.job.log_warning(message=f"Unable to create Device {ids['name']}. {err}")
            return None

    def update(self, attrs):
        """Update device object in Nautobot."""
        dev = OrmDevice.objects.get(id=self.uuid)
        if "device_model" in attrs:
            dev.device_type = nautobot.verify_device_type_object(attrs["device_model"])
        if "serial" in attrs:
            dev.serial = attrs["serial"]
        try:
            dev.validated_save()
            return super().update(attrs)
        except ValidationError as err:
            self.diffsync.job.log_warning(message=f"Unable to update Device {self.name}. {err}")
            return None

    def delete(self):
        """Delete device object in Nautobot."""
        if PLUGIN_SETTINGS.get("delete_devices_on_sync", DEFAULT_DELETE_DEVICES_ON_SYNC):
            self.diffsync.job.log_warning(message=f"Device {self.name} will be deleted per plugin settings.")
            device = OrmDevice.objects.get(id=self.uuid)
            device.delete()
            super().delete()
        return self


class NautobotPort(Port):
    """Nautobot Port model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Interface in Nautobot."""
        device = OrmDevice.objects.get(name=ids["device"])
        new_port = OrmInterface(
            name=ids["name"],
            device=device,
            enabled=is_truthy(attrs["enabled"]),
            mac_address=attrs["mac_addr"],
            mtu=attrs["mtu"],
            mode=attrs["mode"],
            status=OrmStatus.objects.get(slug=attrs["status"]),
            type=attrs["port_type"],
        )
        try:
            new_port.validated_save()
            return super().create(ids=ids, diffsync=diffsync, attrs=attrs)
        except ValidationError as err:
            diffsync.job.log_warning(message=err)
            return None

    def update(self, attrs):
        """Update Interface in Nautobot."""
        _port = OrmInterface.objects.get(id=self.uuid)
        if "mac_addr" in attrs:
            _port.mac_address = attrs["mac_addr"]
        if "mode" in attrs:
            _port.mode = attrs["mode"]
        if "enabled" in attrs:
            _port.enabled = is_truthy(attrs["enabled"])
        if "mtu" in attrs:
            _port.mtu = attrs["mtu"]
        if "status" in attrs:
            _port.status = OrmStatus.objects.get(slug=attrs["status"])
        if "port_type" in attrs:
            _port.type = attrs["port_type"]
        try:
            _port.validated_save()
            return super().update(attrs)
        except ValidationError as err:
            self.diffsync.job.log_warning(
                message=f"Unable to update port {self.name} for {self.device} with {attrs}: {err}"
            )
            return None

    def delete(self):
        """Delete Interface in Nautobot."""
        if PLUGIN_SETTINGS.get("delete_devices_on_sync"):
            super().delete()
            if self.diffsync.job.kwargs.get("debug"):
                self.diffsync.job.log_warning(message=f"Interface {self.name} for {self.device} will be deleted.")
            _port = OrmInterface.objects.get(id=self.uuid)
            _port.delete()
        return self


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
