"""Plugin declaration for aristacv_sync."""

__version__ = "0.1.0"

from nautobot.extras.plugins import PluginConfig

class AristaCVSyncConfig(PluginConfig):
    """Plugin configuration for the aristacv_sync plugin."""

    name = "aristacv_sync"
    verbose_name = "Nautobot to Arista CloudVision Sync"
    version = __version__
    author = "Network to Code, LLC"
    description = "Nautobot to Arista CloudVision Sync."
    base_url = "aristacv-sync"
    required_settings = []
    min_version = "1.0.0"
    max_version = "1.9999"
    default_settings = {}
    caching_config = {}

    def ready(self):
        """Callback invoked after the plugin is loaded."""
        super().ready()

        from nautobot.extras.choices import CustomFieldTypeChoices
        from nautobot.dcim.models import Device
        from nautobot.extras.models import CustomField
        from django.contrib.contenttypes.models import ContentType

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



config = AristaCVSyncConfig  # pylint:disable=invalid-name
