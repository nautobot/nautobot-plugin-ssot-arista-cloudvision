"""DiffSyncModel subclasses for Nautobot-to-AristaCV data sync."""
from uuid import UUID
from diffsync import DiffSyncModel
from typing import List, Optional


class Device(DiffSyncModel):
    """Device Model."""

    _modelname = "device"
    _identifiers = ("name",)
    _attributes = (
        "device_model",
        "serial",
    )
    _children = {"cf": "cfs", "port": "ports"}

    name: str
    device_model: str
    serial: str
    cfs: List["CustomField"] = list()
    ports: List["Port"] = list()
    uuid: Optional[UUID]


class Port(DiffSyncModel):
    """Port Model."""

    _modelname = "port"
    _identifiers = (
        "name",
        "device",
    )
    _attributes = (
        "mac_addr",
        "mtu",
        "type",
        "speed",
        "status",
    )
    _children = {}

    name: str
    device: str
    mac_addr: str
    mtu: Optional[int]
    type: Optional[str]
    speed: Optional[str]
    status: Optional[str]
    uuid: Optional[UUID]


class CustomField(DiffSyncModel):
    """Custom Field model."""

    _modelname = "cf"
    _identifiers = ("name", "device_name")
    _attributes = ("value",)
    _children = {}

    name: str
    value: str
    device_name: str
