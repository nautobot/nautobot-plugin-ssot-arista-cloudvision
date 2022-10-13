"""DiffSync adapter for Nautobot."""
from nautobot.dcim.models import Device as OrmDevice
from nautobot.dcim.models import Interface as OrmInterface
from diffsync import DiffSync
from diffsync.exceptions import ObjectNotFound

from nautobot_ssot_aristacv.diffsync.models.nautobot import NautobotDevice, NautobotCustomField, NautobotPort


class NautobotAdapter(DiffSync):
    """DiffSync adapter implementation for Nautobot custom fields."""

    device = NautobotDevice
    port = NautobotPort
    cf = NautobotCustomField

    top_level = ["device", "cf"]

    def __init__(self, *args, job=None, **kwargs):
        """Initialize the Nautobot DiffSync adapter."""
        super().__init__(*args, **kwargs)
        self.job = job

    def load(self):
        """Load device custom field data from Nautobot and populate DiffSync models."""
        devices = OrmDevice.objects.all()
        for dev in devices:
            try:
                if dev.device_type.manufacturer.name.lower() == "arista":
                    new_device = self.device(
                        name=dev.name, device_model=dev.device_type.name, serial=dev.serial, uuid=dev.id
                    )
                    self.add(new_device)
                    dev_custom_fields = dev.custom_field_data

                    for cf_name, cf_value in dev_custom_fields.items():
                        if cf_value is None:
                            cf_value = ""
                        new_cf = self.cf(name=cf_name, value=cf_value, device_name=dev.name)
                        self.add(new_cf)

                    # Gets model from device and puts it into CustomField Object.
                    new_cf = self.cf(name="arista_model", value=str(dev.platform), device_name=dev.name)
                    self.add(new_cf)
            except AttributeError:
                continue

        for intf in OrmInterface.objects.all():
            new_port = self.port(
                name=intf.name,
                device=intf.device.name,
                mac_addr=intf.mac_address if intf.mac_address else "",
                enabled=intf.enabled,
                mode=intf.mode,
                mtu=intf.mtu,
                port_type=intf.type,
                status=intf.status.slug,
                uuid=intf.id,
            )
            self.add(new_port)
            try:
                dev = self.get(self.device, intf.device.name)
                dev.add_child(new_port)
            except ObjectNotFound as err:
                self.job.log_warning(
                    message=f"Unable to find Device {intf.device.name} in diff to assign to port {intf.name}. {err}"
                )
