"""DiffSync adapter for Arista CloudVision."""
import distutils
import re

import arista.tag.v1 as TAG
from diffsync import DiffSync
from diffsync.exceptions import ObjectAlreadyExists
from django.forms import ValidationError
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

    def load(self):
        """Load tag data from CloudVision."""
        devices = cloudvision.get_devices(client=self.conn.comm_channel)
        system_tags = cloudvision.get_tags_by_type(
            client=self.conn.comm_channel, creator_type=TAG.models.CREATOR_TYPE_SYSTEM
        )

        for dev in devices:
            new_device = None
            if dev["hostname"] != "":
                chassis_type = cloudvision.get_device_type(client=self.conn, dId=dev["device_id"])
                if self.job.kwargs.get("debug"):
                    self.job.log_debug(message=f"Chassis type for {dev['hostname']} is {chassis_type}.")
                port_info = []
                if chassis_type == "modular":
                    port_info = cloudvision.get_interfaces_chassis(client=self.conn, dId=dev["device_id"])
                elif chassis_type == "fixedSystem":
                    port_info = cloudvision.get_interfaces_fixed(client=self.conn, dId=dev["device_id"])
                if self.job.kwargs.get("debug"):
                    self.job.log_debug(message=f"Device being loaded: {dev}. Port: {port_info}.")
                new_device = self.device(
                    name=dev["hostname"], serial=dev["device_id"], device_model=dev["model"], uuid=None
                )
                try:
                    self.add(new_device)
                except ValidationError as err:
                    self.job.log_warning(message=f"Unable to load Device {dev['hostname']}. {err}")
                    continue
                except ObjectAlreadyExists as err:
                    self.job.log_warning(
                        message=f"Duplicate device {dev['hostname']} {dev['device_id']} found and ignored. {err}"
                    )
                    continue

                for port in port_info:
                    if self.job.kwargs.get("debug"):
                        self.job.log_debug(message=f"Port {port['interface']} being loaded for {dev['hostname']}.")
                    port_mode = cloudvision.get_interface_mode(client=self.conn, dId=dev["device_id"], interface=port)
                    transceiver = cloudvision.get_interface_transceiver(
                        client=self.conn, dId=dev["device_id"], interface=port
                    )
                    port_status = cloudvision.get_interface_status(port_info=port)
                    port_type = cloudvision.get_port_type(port_info=port, transceiver=transceiver)
                    if port["interface"] != "":
                        new_port = self.port(
                            name=port["interface"],
                            device=dev["hostname"],
                            mac_addr=port["mac_addr"],
                            mode="tagged" if port_mode == "trunk" else "access",
                            mtu=port["mtu"],
                            enabled=port["enabled"],
                            status=port_status,
                            port_type=port_type,
                            uuid=None,
                        )
                        try:
                            self.add(new_port)
                            new_device.add_child(new_port)
                        except ObjectAlreadyExists as err:
                            self.job.log_warning(
                                message=f"Duplicate port {port['interface']} found for {dev['hostname']} and ignored. {err}"
                            )
            else:
                self.job.log_warning(message=f"Device {dev} is missing hostname so won't be imported.")
                continue

            dev_tags = [
                tag
                for tag in cloudvision.get_device_tags(client=self.conn.comm_channel, device_id=dev["device_id"])
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

                new_cf = self.cf(name=f"arista_{tag['label']}", value=tag["value"], device_name=dev["hostname"])
                try:
                    self.add(new_cf)
                except ObjectAlreadyExists:
                    self.job.log_warning(
                        message=f"Duplicate tag encountered for {tag['label']} on device {dev['hostname']}"
                    )
