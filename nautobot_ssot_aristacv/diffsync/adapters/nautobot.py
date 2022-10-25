"""DiffSync adapter for Nautobot."""
from nautobot.dcim.models import Device as OrmDevice
from nautobot.dcim.models import Interface as OrmInterface
from nautobot.ipam.models import IPAddress as OrmIPAddress
from diffsync import DiffSync
from diffsync.exceptions import ObjectNotFound, ObjectAlreadyExists

from nautobot_ssot_aristacv.diffsync.models.nautobot import (
    NautobotDevice,
    NautobotCustomField,
    NautobotIPAddress,
    NautobotPort,
)
from nautobot_ssot_aristacv.utils import nautobot


class NautobotAdapter(DiffSync):
    """DiffSync adapter implementation for Nautobot custom fields."""

    device = NautobotDevice
    port = NautobotPort
    ipaddr = NautobotIPAddress
    cf = NautobotCustomField

    top_level = ["device", "ipaddr", "cf"]

    def __init__(self, *args, job=None, **kwargs):
        """Initialize the Nautobot DiffSync adapter."""
        super().__init__(*args, **kwargs)
        self.job = job

    def load(self):
        """Load device custom field data from Nautobot and populate DiffSync models."""
        for dev in OrmDevice.objects.filter(device_type__manufacturer__slug="arista"):
            try:
                new_device = self.device(
                    name=dev.name,
                    device_model=dev.device_type.model,
                    serial=dev.serial,
                    status=dev.status.slug,
                    version=nautobot.get_device_version(dev),
                    uuid=dev.id,
                )
                self.add(new_device)
            except ObjectAlreadyExists as err:
                self.job.log_warning(message=f"Unable to load {dev.name} as it appears to be a duplicate. {err}")
                continue

            for cf_name, cf_value in dev.custom_field_data.items():
                if cf_name.startswith("arista_"):
                    try:
                        new_cf = self.cf(
                            name=cf_name, value=cf_value if cf_value is not None else "", device_name=dev.name
                        )
                        self.add(new_cf)
                    except AttributeError as err:
                        self.job.log_warning(message=f"Unable to load {cf_name}. {err}")
                        continue

        for intf in OrmInterface.objects.filter(device__device_type__manufacturer__slug="arista"):
            new_port = self.port(
                name=intf.name,
                device=intf.device.name,
                description=intf.description,
                mac_addr=str(intf.mac_address).lower() if intf.mac_address else "",
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

        for ipaddr in OrmIPAddress.objects.filter(interface__device__device_type__manufacturer__slug="arista"):
            new_ip = self.ipaddr(
                address=str(ipaddr.address),
                interface=ipaddr.assigned_object.name,
                device=ipaddr.assigned_object.device.name,
                uuid=ipaddr.id,
            )
            try:
                self.add(new_ip)
            except ObjectAlreadyExists as err:
                self.job.log_warning(message=f"Unable to load {ipaddr.address} as appears to be a duplicate. {err}")
