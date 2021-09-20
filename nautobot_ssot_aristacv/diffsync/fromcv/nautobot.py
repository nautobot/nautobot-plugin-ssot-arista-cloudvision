"""DiffSync adapter for Nautobot."""
from nautobot.dcim.models import Device as NautobotDevice
from diffsync import DiffSync

from .models import Device, CustomField


class Nautobot(DiffSync):
    """DiffSync adapter implementation for Nautobot custom fields."""

    device = Device
    cf = CustomField

    top_level = ["device"]

    def __init__(self, *args, job=None, **kwargs):
        """Initialize the Nautobot DiffSync adapter."""
        super().__init__(*args, **kwargs)
        self.job = job

    def load(self):
        """Load device custom field data from Nautobot and populate DiffSync models."""
        devices = NautobotDevice.objects.all()
        for dev in devices:
            try:
                if dev.device_type.manufacturer.name.lower() == "arista":
                    self.device = Device(name=dev.name)
                    self.add(self.device)
                    dev_custom_fields = dev.custom_field_data

                    for cf_name, cf_value in dev_custom_fields.items():
                        if cf_value is None:
                            cf_value = ""
                        self.cf = CustomField(name=cf_name, value=cf_value, device_name=dev.name)
                        self.add(self.cf)
                        self.device.add_child(self.cf)

                    # Gets model from device and puts it into CustomField Object.
                    self.cf = CustomField(name="arista_model", value=str(dev.platform), device_name=dev.name)
                    self.add(self.cf)
                    self.device.add_child(self.cf)
            except AttributeError:
                continue
