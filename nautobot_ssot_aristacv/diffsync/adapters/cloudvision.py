"""DiffSync adapter for Arista CloudVision."""
import distutils
import re

import arista.tag.v1 as TAG
from diffsync import DiffSync
from diffsync.exceptions import ObjectAlreadyExists
from nautobot_ssot_aristacv.diffsync.models.cloudvision import (
    CloudvisionCustomField,
    CloudvisionDevice,
    CloudvisionPort,
)
from nautobot_ssot_aristacv.utils import cloudvision


class CloudvisionAdapter(DiffSync):
    """DiffSync adapter implementation for CloudVision user-defined device tags."""

    device = CloudvisionDevice
    port = CloudvisionPort
    cf = CloudvisionCustomField

    top_level = ["device", "cf"]

    def __init__(self, *args, job=None, conn: cloudvision.CloudvisionApi, **kwargs):
        """Initialize the CloudVision DiffSync adapter."""
        super().__init__(*args, **kwargs)
        self.job = job
        self.conn = conn

    def load_devices(self):
        """Load devices from CloudVision."""
        for dev in cloudvision.get_devices(client=self.conn.comm_channel):
            if dev["hostname"] != "":
                new_device = self.device(
                    name=dev["hostname"], serial=dev["device_id"], device_model=dev["model"], uuid=None
                )
                try:
                    self.add(new_device)
                except ObjectAlreadyExists as err:
                    self.job.log_warning(
                        message=f"Duplicate device {dev['hostname']} {dev['device_id']} found and ignored. {err}"
                    )
                    continue
                self.load_interfaces(device=new_device)
                self.load_device_tags(device=new_device)
            else:
                self.job.log_warning(message=f"Device {dev} is missing hostname so won't be imported.")
                continue

    def load_interfaces(self, device):
        """Load device interface from CloudVision."""
        chassis_type = cloudvision.get_device_type(client=self.conn, dId=device.serial)
        if self.job.kwargs.get("debug"):
            self.job.log_debug(message=f"Chassis type for {device.name} is {chassis_type}.")
        port_info = []
        if chassis_type == "modular":
            port_info = cloudvision.get_interfaces_chassis(client=self.conn, dId=device.serial)
        elif chassis_type == "fixedSystem":
            port_info = cloudvision.get_interfaces_fixed(client=self.conn, dId=device.serial)
        if self.job.kwargs.get("debug"):
            self.job.log_debug(message=f"Device being loaded: {device.name}. Port: {port_info}.")
        for port in port_info:
            if self.job.kwargs.get("debug"):
                self.job.log_debug(message=f"Port {port['interface']} being loaded for {device.name}.")
            port_mode = cloudvision.get_interface_mode(client=self.conn, dId=device.serial, interface=port)
            transceiver = cloudvision.get_interface_transceiver(client=self.conn, dId=device.serial, interface=port)
            if transceiver == "Unknown":
                # Breakout transceivers, ie 40G -> 4x10G, shows up as 4 interfaces and requires looking at base interface to find transceiver, ie Ethernet1 if Ethernet1/1
                base_port_name = re.sub(r"/\d", "", port["interface"])
                transceiver = cloudvision.get_interface_transceiver(
                    client=self.conn, dId=device.serial, interface=base_port_name
                )
            port_status = cloudvision.get_interface_status(port_info=port)
            port_type = cloudvision.get_port_type(port_info=port, transceiver=transceiver)
            if port["interface"] != "":
                new_port = self.port(
                    name=port["interface"],
                    device=device.name,
                    mac_addr=port["mac_addr"] if port.get("mac_addr") else "",
                    mode="tagged" if port_mode == "trunk" else "access",
                    mtu=port["mtu"],
                    enabled=port["enabled"],
                    status=port_status,
                    port_type=port_type,
                    uuid=None,
                )
                try:
                    self.add(new_port)
                    device.add_child(new_port)
                except ObjectAlreadyExists as err:
                    self.job.log_warning(
                        message=f"Duplicate port {port['interface']} found for {device.name} and ignored. {err}"
                    )

    def load_device_tags(self, device):
        """Load device tags from CloudVision."""
        system_tags = cloudvision.get_tags_by_type(
            client=self.conn.comm_channel, creator_type=TAG.models.CREATOR_TYPE_SYSTEM
        )
        dev_tags = [
            tag
            for tag in cloudvision.get_device_tags(client=self.conn.comm_channel, device_id=device.serial)
            if tag in system_tags
        ]

        # Check if topology_type tag exists
        list_of_tag_names = [value["label"] for value in dev_tags]
        if "topology_type" not in list_of_tag_names:
            dev_tags.append({"label": "topology_type", "value": "-"})

        for tag in dev_tags:
            if tag["label"] in ["hostname", "serialnumber", "Container"]:
                continue
            if tag["label"] == "mpls" or tag["label"] == "ztp":
                tag["value"] = bool(distutils.util.strtobool(tag["value"]))

            new_cf = self.cf(name=f"arista_{tag['label']}", value=tag["value"], device_name=device.name)
            try:
                self.add(new_cf)
            except ObjectAlreadyExists:
                self.job.log_warning(message=f"Duplicate tag encountered for {tag['label']} on device {device.name}")

    def load(self):
        """Load devices and associated data from CloudVision."""
        self.load_devices()
