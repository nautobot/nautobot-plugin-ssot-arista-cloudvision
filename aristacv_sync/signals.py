"""Nautobot signal handler functions for aristavc_sync."""

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from nautobot.extras.choices import CustomFieldTypeChoices

def post_migrate_create_custom_fields(apps, **kwargs):
    """Callback function for post_migrate() -- create CustomField records."""
    ContentType = apps.get_model("contenttypes", "ContentType")
    Device = apps.get_model("dcim", "Device")
    CustomField = apps.get_model("extras", "CustomField")

    for device_cf_dict in [
            {
                "name": "eostrain",
                "type": CustomFieldTypeChoices.TYPE_TEXT,
                "label": "EOS Train",
            },
            {
                "name": "eos",
                "type": CustomFieldTypeChoices.TYPE_TEXT,
                "label": "EOS Version",
            },
            {
                "name": "ztp",
                "type": CustomFieldTypeChoices.TYPE_BOOLEAN,
                "label": "ztp",
            },
            {
                "name": "pimbidir",
                "type": CustomFieldTypeChoices.TYPE_TEXT,
                "label": "pimbidir",
            },
            {
                "name": "pim",
                "type": CustomFieldTypeChoices.TYPE_TEXT,
                "label": "pim",
            },
            {
                "name": "bgp",
                "type": CustomFieldTypeChoices.TYPE_TEXT,
                "label": "bgp",
            },
            {
                "name": "mpls",
                "type": CustomFieldTypeChoices.TYPE_BOOLEAN,
                "label": "mpls",
            },
            {
                "name": "systype",
                "type": CustomFieldTypeChoices.TYPE_TEXT,
                "label": "systype",
            },
            {
                "name": "mlag",
                "type": CustomFieldTypeChoices.TYPE_TEXT,
                "label": "MLAG",
            },
            {
                "name": "tapagg",
                "type": CustomFieldTypeChoices.TYPE_TEXT,
                "label": "TAP Aggregation",
            },
            {
                "name": "sflow",
                "type": CustomFieldTypeChoices.TYPE_TEXT,
                "label": "sFlow",
            },
            {
                "name": "terminattr",
                "type": CustomFieldTypeChoices.TYPE_TEXT,
                "label": "TerminAttr Version",
            },
            {
                "name": "topology_network_type",
                "type": CustomFieldTypeChoices.TYPE_TEXT,
                "label": "Topology Network Type",
            },
        ]:
            field, _ = CustomField.objects.get_or_create(name=device_cf_dict["name"], defaults=device_cf_dict)
            field.content_types.set([ContentType.objects.get_for_model(Device)])