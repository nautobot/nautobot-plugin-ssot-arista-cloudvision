"""Diffsync models for Nautobot <-> CloudVision sync."""

from diffsync import DiffSyncModel
from typing import List, Optional


class Device(DiffSyncModel):
    """Device Model"""

    _modelname = "device"
    _identifiers = ("name",)
    _attributes = ()
    _children = {"tag": "tags"}

    name: str
    device_id: str
    tags: List = list()


class Tag(DiffSyncModel):
    """Tag model"""

    _modelname = "tag"
    _identifiers = ("name", "value", "device_name")
    _shortname = ("name",)
    _attributes = ()

    name: str
    device_name: str
    value: str
    tag_type: str
