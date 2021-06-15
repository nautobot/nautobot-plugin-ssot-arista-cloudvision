"""Utility functions for CloudVision Resource API."""
import os

import grpc
import arista.inventory.v1 as inv
import arista.tag.v1 as tag
from google.protobuf import wrappers_pb2 as wrappers

RPC_TIMEOUT = 30

cvp_url = os.environ.get("CVP_URL", "www.arista.io:443")
call_creds = grpc.access_token_call_credentials(os.environ["CVP_TOKEN"])
channel_creds = grpc.ssl_channel_credentials()
conn_creds = grpc.composite_channel_credentials(channel_creds, call_creds)


def get_devices():
    """Get active devices from CloudVision inventory."""
    with grpc.secure_channel(cvp_url, conn_creds) as channel:
        device_stub = inv.services.DeviceServiceStub(channel)
        req = inv.services.DeviceStreamRequest(
            partial_eq_filter=[inv.models.Device(streaming_status=inv.models.STREAMING_STATUS_ACTIVE)]
        )
        responses = device_stub.GetAll(req)
        devices = list()
        for resp in responses:
            device = {
                "device_id": resp.value.key.device_id.value,
                "hostname": resp.value.hostname.value,
                "fqdn": resp.value.fqdn.value,
                "sw_ver": resp.value.software_version.value,
                "model": resp.value.model_name.value,
                "system_mac_address": resp.value.system_mac_address.value,
            }
            devices.append(device)
    return devices


def get_device_id(device_name: str):
    """Get device_id for device_name from CloudVision inventory."""
    with grpc.secure_channel(cvp_url, conn_creds) as channel:
        device_stub = inv.services.DeviceServiceStub(channel)
        req = inv.services.DeviceStreamRequest(
            partial_eq_filter=[
                inv.models.Device(hostname=device_name, streaming_status=inv.models.STREAMING_STATUS_ACTIVE)
            ]
        )
        resp = device_stub.Get(req)
    return resp.value.key.device_id.value


def get_tags():
    """Get all tags from CloudVision."""
    with grpc.secure_channel(cvp_url, conn_creds) as channel:
        tag_stub = tag.services.DeviceTagServiceStub(channel)
        req = tag.services.DeviceTagStreamRequest()
        responses = tag_stub.GetAll(req)
        tags = list()
        for resp in responses:
            dev_tag = {
                "label": resp.value.key.label.value,
                "value": resp.value.key.value.value,
                "creator_type": resp.value.creator_type,
            }
            tags.append(dev_tag)
    return tags


def get_tags_by_type(creator_type: int = tag.models.CREATOR_TYPE_USER):
    """Get tags by creator type from CloudVision."""
    with grpc.secure_channel(cvp_url, conn_creds) as channel:
        tag_stub = tag.services.DeviceTagServiceStub(channel)
        req = tag.services.DeviceTagStreamRequest(partial_eq_filter=[tag.models.DeviceTag(creator_type=creator_type)])
        responses = tag_stub.GetAll(req)
        tags = list()
        for resp in responses:
            dev_tag = {
                "label": resp.value.key.label.value,
                "value": resp.value.key.value.value,
            }
            tags.append(dev_tag)
    return tags


def get_device_tags(device_id: str):
    """Get tags for specific device."""
    with grpc.secure_channel(cvp_url, conn_creds) as channel:
        tag_stub = tag.services.DeviceTagAssignmentConfigServiceStub(channel)
        req = tag.services.DeviceTagAssignmentConfigStreamRequest(
            partial_eq_filter=[
                tag.models.DeviceTagAssignmentConfig(
                    key=tag.models.DeviceTagAssignmentKey(
                        device_id=wrappers.StringValue(value=device_id),
                    )
                )
            ]
        )
        responses = tag_stub.GetAll(req)
        tags = list()
        for resp in responses:
            dev_tag = {
                "label": resp.value.key.label.value,
                "value": resp.value.key.value.value,
            }
            tags.append(dev_tag)
    return tags


def create_tag(label: str, value: str):
    """Create user-defined tag in CloudVision."""
    with grpc.secure_channel(cvp_url, conn_creds) as channel:
        tag_stub = tag.services.DeviceTagConfigServiceStub(channel)
        req = tag.services.DeviceTagConfigSetRequest(
            value=tag.models.DeviceTagConfig(
                key=tag.models.TagKey(label=wrappers.StringValue(value=label), value=wrappers.StringValue(value=value))
            )
        )
        try:
            tag_stub.Set(req)
        except grpc.RpcError as e:
            # Ignore RPC error if tag already exists for idempotency
            if e.code() != grpc.StatusCode.ALREADY_EXISTS:
                raise e


def delete_tag(label: str, value: str):
    """Delete user-defined tag in CloudVision."""
    with grpc.secure_channel(cvp_url, conn_creds) as channel:
        tag_stub = tag.services.DeviceTagConfigServiceStub(channel)
        req = tag.services.DeviceTagConfigDeleteRequest(
            key=tag.models.TagKey(label=wrappers.StringValue(value=label), value=wrappers.StringValue(value=value))
        )
        try:
            tag_stub.Delete(req)
        # Skip error of tags that may be assigned to devices manually in CloudVision
        except grpc.RpcError as e:
            if e.details() != "assignments for this tag exist":
                raise e


def assign_tag_to_device(device_id: str, label: str, value: str):
    """Assign user-defined tag to device in CloudVision."""
    with grpc.secure_channel(cvp_url, conn_creds) as channel:
        tag_stub = tag.services.DeviceTagAssignmentConfigServiceStub(channel)
        req = tag.services.DeviceTagAssignmentConfigSetRequest(
            value=tag.models.DeviceTagAssignmentConfig(
                key=tag.models.DeviceTagAssignmentKey(
                    label=wrappers.StringValue(value=label),
                    value=wrappers.StringValue(value=value),
                    device_id=wrappers.StringValue(value=device_id),
                )
            )
        )
        tag_stub.Set(req)


def remove_tag_from_device(device_id: str, label: str, value: str):
    """Unassign a tag from a device in CloudVision."""
    with grpc.secure_channel(cvp_url, conn_creds) as channel:
        tag_stub = tag.services.DeviceTagAssignmentConfigServiceStub(channel)
        req = tag.services.DeviceTagAssignmentConfigDeleteRequest(
            key=tag.models.DeviceTagAssignmentKey(
                label=wrappers.StringValue(value=label),
                value=wrappers.StringValue(value=value),
                device_id=wrappers.StringValue(value=device_id),
            )
        )
        tag_stub.Delete(req, timeout=RPC_TIMEOUT)
