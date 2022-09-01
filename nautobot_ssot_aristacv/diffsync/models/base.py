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
    _children = {"cf": "cfs"}

    name: str
    device_model: str
    serial: str
    cfs: List["CustomField"] = list()
    uuid: Optional[UUID]


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
