"""Utility functions for Nautobot ORM."""
from nautobot.dcim.models import DeviceType, DeviceRole, Site, Manufacturer
from nautobot.extras.models.statuses import Status
from nautobot.extras.models.customfields import CustomField


def verify_site(site_name):
    """Verifies whether site in plugin config is created. If not, creates site.

    Args:
        site_name (str): Name of the site.
    """
    try:
        site_obj = Site.objects.get(name=site_name)
    except Site.DoesNotExist:
        site_obj = Site(name=site_name, slug=site_name.lower(), status=Status.objects.get(name="Staging"))
        site_obj.validated_save()
    return site_obj


def verify_manufacturer():
    """Verifies whether Arista manufactere exists in Nautobot. If not, creates Arista Manufacturer."""
    try:
        arista_mf = Manufacturer.objects.get(name="Arista")
    except Manufacturer.DoesNotExist:
        arista_mf = Manufacturer(name="Arista", slug="arista")
        arista_mf.validated_save()
    return arista_mf


def verify_device_type_object(device_type):
    """Verifies whether device type object already exists in Nautobot. If not, creates specified device type.

    Args:
        device_type (str): Device model gathered from Cloudvision.
    """
    try:
        device_type_obj = DeviceType.objects.get(model=device_type)
    except DeviceType.DoesNotExist:
        mf = verify_manufacturer()
        device_type_obj = DeviceType(manufacturer=mf, model=device_type, slug=device_type.lower())
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


def assign_arista_cf(device):
    """Assigns arista custom fields to device."""
    for cf in CustomField.objects.filter(name__contains="arista"):
        device.cf[cf.name] = cf.default

    return device
