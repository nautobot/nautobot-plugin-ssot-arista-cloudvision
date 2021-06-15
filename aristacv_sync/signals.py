"""Nautobot signal handler functions for aristacv_sync."""

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from nautobot.extras.choices import CustomFieldTypeChoices
from nautobot.extras.choices import RelationshipTypeChoices
from nautobot.dcim.models import Device
from nautobot.extras.models import CustomField
from django.contrib.contenttypes.models import ContentType

def post_migrate_create_custom_fields(**kwargs):
    """Callback function for post_migrate() -- create CustomField records."""

    # ContentType = apps.get_model("contenttypes", "ContentType")
    # Device = apps.get_model("dcim", "Device")
    # CustomField = apps.get_model("extras", "CustomField")

    for device_cf_dict in [
        {
            "name": "eos_train",
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "label": "EOS Train",
        },
        {
            "name": "eos_version",
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
            "type": CustomFieldTypeChoices.TYPE_BOOLEAN,
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
            "name": "serial_number",
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "label": "Serial Number",
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
            "name": "terminatr",
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "label": "TerminAttr Version",
        },
    ]:
        field, _ = CustomField.objects.get_or_create(name=device_cf_dict["name"], defaults=device_cf_dict)
        field.content_types.set([ContentType.objects.get_for_model(Device)])