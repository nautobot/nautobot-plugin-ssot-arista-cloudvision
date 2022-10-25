"""Utility functions for Nautobot ORM."""
import re
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify

from nautobot.dcim.models import DeviceRole, DeviceType, Manufacturer, Site
from nautobot.extras.models import Status, Tag, Relationship

try:
    from nautobot_device_lifecycle_mgmt.models import SoftwareLCM  # noqa: F401 # pylint: disable=unused-import

    LIFECYCLE_MGMT = True
except ImportError:
    print("Device Lifecycle plugin isn't installed so will revert to CustomField for OS version.")
    LIFECYCLE_MGMT = False


def verify_site(site_name):
    """Verifies whether site in plugin config is created. If not, creates site.

    Args:
        site_name (str): Name of the site.
    """
    try:
        site_obj = Site.objects.get(name=site_name)
    except Site.DoesNotExist:
        site_obj = Site(name=site_name, slug=slugify(site_name), status=Status.objects.get(name="Staging"))
        site_obj.validated_save()
    return site_obj


def verify_device_type_object(device_type):
    """Verifies whether device type object already exists in Nautobot. If not, creates specified device type.

    Args:
        device_type (str): Device model gathered from Cloudvision.
    """
    try:
        device_type_obj = DeviceType.objects.get(model=device_type)
    except DeviceType.DoesNotExist:
        device_type_obj = DeviceType(
            manufacturer=Manufacturer.objects.get(name="Arista"), model=device_type, slug=device_type.lower()
        )
        device_type_obj.validated_save()
    return device_type_obj


def verify_device_role_object(role_name, role_color):
    """Verifies device role object exists in Nautobot. If not, creates specified device role.

    Args:
        role_name (str): Role name.
        role_color (str): Role color.
    """
    try:
        role_obj = DeviceRole.objects.get(name=role_name)
    except DeviceRole.DoesNotExist:
        role_obj = DeviceRole(name=role_name, slug=role_name.lower(), color=role_color)
        role_obj.validated_save()
    return role_obj


def verify_device_status(device_status, device_status_color):
    """Verifies device status object exists in Nautobot. If not, creates specified device status.

    Args:
        device_status (str): Status name.
        device_status_color (str): Status color.
    """
    try:
        status_obj = Status.objects.get(name=device_status)
    except Status.DoesNotExist:
        dcim_device = ContentType.objects.get(app_label="dcim", model="device")
        status_obj = Status(
            name=device_status,
            slug=device_status.lower(),
            color=device_status_color,
            description="Devices imported from CloudVision.",
        )
        status_obj.validated_save()
        status_obj.content_types.set([dcim_device])
    return status_obj


def verify_import_tag():
    """Verify `cloudvision_imported` tag exists. if not, creates the tag."""
    try:
        import_tag = Tag.objects.get(name="cloudvision_imported")
    except Tag.DoesNotExist:
        import_tag = Tag(name="cloudvision_imported", slug="cloudvision_imported", color="ff0000")
        import_tag.validated_save()
    return import_tag


def get_device_version(device):
    """Determines Device version from Custom Field or RelationshipAssociation.

    Args:
        device (Device): The Device object to determine software version for.
    """
    version = ""
    if LIFECYCLE_MGMT:
        software_relation = Relationship.objects.get(name="Software on Device")
        relations = device.get_relationships()
        try:
            version = relations["destination"][software_relation][0].source.version
        except KeyError:
            pass
    else:
        version = device.custom_field_data["arista_eos"]
    return version


def parse_hostname(hostname: str):
    """Parse a device's hostname to find site and role.

    Args:
        hostname (str): Device hostname to be parsed for site and role.
    """
    hostname_patterns = settings.PLUGINS_CONFIG["nautobot_ssot_aristacv"].get("hostname_patterns")

    site, role = None, None
    for pattern in hostname_patterns:
        match = re.search(pattern=pattern, string=hostname)
        if match:
            if match.group("site"):
                site = match.group("site")
            if match.group("role"):
                role = match.group("role")
    return (site, role)


def get_site_from_map(site_code: str):
    """Get name of Site from site_mapping based upon sitecode.

    Args:
        site_code (str): Site code from device hostname.

    Returns:
        str|None: Name of Site if site code found else None.
    """
    site_map = settings.PLUGINS_CONFIG["nautobot_ssot_aristacv"].get("site_mappings")
    site_name = None
    if site_code in site_map:
        site_name = site_map[site_code]
    return site_name


def get_role_from_map(role_code: str):
    """Get name of Role from role_mapping based upon role code in hostname.

    Args:
        role_code (str): Role code from device hostname.

    Returns:
        str|None: Name of Device Role if role code found else None.
    """
    role_map = settings.PLUGINS_CONFIG["nautobot_ssot_aristacv"].get("role_mappings")
    role_name = None
    if role_code in role_map:
        role_name = role_map[role_code]
    return role_name
