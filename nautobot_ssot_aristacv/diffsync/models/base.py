"""DiffSyncModel subclasses for Nautobot-to-AristaCV data sync."""
from diffsync import DiffSyncModel
from typing import List, Optional


class Device(DiffSyncModel):
    """Device Model."""

    _modelname = "device"
    _identifiers = ("name",)
    _shortname = ()
    _attributes = ("device_model",)
    _children = {"cf": "cfs"}

    name: str
    cfs: List = list()
    device_model: str


class CustomField(DiffSyncModel):
    """Custom Field model."""

    _modelname = "cf"
    _identifiers = ("name", "device_name")
    _shortname = ()
    _attributes = ("value",)

    name: str
    value: str
    device_name: str
