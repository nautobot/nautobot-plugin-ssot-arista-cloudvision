# pylint: disable=invalid-name
"""Nautobot signal handler functions for aristavc_sync."""

from django.apps import apps as global_apps
from nautobot.extras.choices import CustomFieldTypeChoices


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
        field, _ = CustomField.objects.get_or_create(name=device_cf_dict["name"], defaults=device_cf_dict)
        field.content_types.set([ContentType.objects.get_for_model(Device)])
