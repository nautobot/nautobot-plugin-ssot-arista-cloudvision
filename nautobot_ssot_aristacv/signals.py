# pylint: disable=invalid-name
"""Nautobot signal handler functions for aristavc_sync."""

from django.apps import apps as global_apps
from django.conf import settings
from django.utils.text import slugify
from nautobot.extras.choices import CustomFieldTypeChoices, RelationshipTypeChoices


def post_migrate_create_custom_fields(apps=global_apps, **kwargs):
    """Callback function for post_migrate() -- create CustomField records."""
    ContentType = apps.get_model("contenttypes", "ContentType")
    Device = apps.get_model("dcim", "Device")
    CustomField = apps.get_model("extras", "CustomField")

    for device_cf_dict in [
        {
            "name": "arista_eostrain",
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "label": "EOS Train",
        },
        {
            "name": "arista_eos",
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "label": "EOS Version",
        },
        {
            "name": "arista_ztp",
            "type": CustomFieldTypeChoices.TYPE_BOOLEAN,
            "label": "ztp",
        },
        {
            "name": "arista_pimbidir",
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "label": "pimbidir",
        },
        {
            "name": "arista_pim",
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "label": "pim",
        },
        {
            "name": "arista_bgp",
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "label": "bgp",
        },
        {
            "name": "arista_mpls",
            "type": CustomFieldTypeChoices.TYPE_BOOLEAN,
            "label": "mpls",
        },
        {
            "name": "arista_systype",
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "label": "systype",
        },
        {
            "name": "arista_mlag",
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "label": "mlag",
        },
        {
            "name": "arista_tapagg",
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "label": "TAP Aggregation",
        },
        {
            "name": "arista_sflow",
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "label": "sFlow",
        },
        {
            "name": "arista_terminattr",
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "label": "TerminAttr Version",
        },
        {
            "name": "arista_topology_network_type",
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "label": "Topology Network Type",
        },
        {"name": "arista_topology_type", "type": CustomFieldTypeChoices.TYPE_TEXT, "label": "Topology Type"},
    ]:
        field, _ = CustomField.objects.get_or_create(
            name=device_cf_dict["name"], defaults=device_cf_dict, slug=device_cf_dict["name"]
        )
        field.content_types.set([ContentType.objects.get_for_model(Device)])


def post_migrate_create_manufacturer(apps=global_apps, **kwargs):
    """Callback function for post_migrate() -- create Arista Manufacturer."""
    Manufacturer = apps.get_model("dcim", "Manufacturer")
    Manufacturer.objects.get_or_create(name="Arista", slug="arista")


def post_migrate_create_platform(apps=global_apps, **kwargs):
    """Callback function for post_migrate() -- create Arista Platform."""
    Platform = apps.get_model("dcim", "Platform")
    Manufacturer = apps.get_model("dcim", "Manufacturer")
    Platform.objects.get_or_create(
        name="arista.eos.eos",
        slug="arista_eos",
        napalm_driver="eos",
        manufacturer=Manufacturer.objects.get(slug="arista"),
    )


def post_migrate_create_controller_device(apps=global_apps, **kwargs):
    """Callback function for post_migrate() -- create CloudVision controller Device."""
    Device = apps.get_model("dcim", "Device")
    DeviceType = apps.get_model("dcim", "DeviceType")
    DeviceRole = apps.get_model("dcim", "DeviceRole")
    Manufacturer = apps.get_model("dcim", "Manufacturer")
    Site = apps.get_model("dcim", "Site")
    Status = apps.get_model("extras", "Status")

    PLUGIN_CFG = settings.PLUGINS_CONFIG["nautobot_ssot_aristacv"]
    if PLUGIN_CFG.get("controller_site") and PLUGIN_CFG["controller_site"] != "":
        site_name = PLUGIN_CFG["controller_site"]
    else:
        site_name = "CloudVision"

    device_type, _ = DeviceType.objects.get_or_create(
        model="CloudVision",
        manufacturer=Manufacturer.objects.get(slug="arista"),
    )
    device_role, _ = DeviceRole.objects.get_or_create(
        name="Controller",
        slug="controller",
        description="Device that controls another Device",
        vm_role=True,
    )
    status, _ = Status.objects.get_or_create(name="Active", slug="active")
    try:
        site = Site.objects.get(name=site_name)
    except Site.DoesNotExist:
        site, _ = Site.objects.get_or_create(name=site_name, slug=slugify(site_name), status=status)
    Device.objects.get_or_create(
        name="CloudVision",
        device_role=device_role,
        device_type=device_type,
        site=site,
        status=status,
    )


def post_migrate_create_controller_relationship(apps=global_apps, **kwargs):
    """Callback function for post_migrate() -- create Relationship for Controller -> Device."""
    Device = apps.get_model("dcim", "Device")
    Relationship = apps.get_model("extras", "Relationship")
    ContentType = apps.get_model("contenttypes", "ContentType")
    relationship_dict = {
        "name": "Controller -> Device",
        "slug": "controller_to_device",
        "type": RelationshipTypeChoices.TYPE_ONE_TO_MANY,
        "source_type": ContentType.objects.get_for_model(Device),
        "source_label": "Controller",
        "destination_type": ContentType.objects.get_for_model(Device),
        "destination_label": "Device",
    }
    Relationship.objects.get_or_create(name=relationship_dict["name"], defaults=relationship_dict)
