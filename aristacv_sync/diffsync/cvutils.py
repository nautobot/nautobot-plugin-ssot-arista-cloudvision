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


def get_tags():
    """Get all tags from CloudVision."""
    with grpc.secure_channel(cvp_url, conn_creds) as channel:
        tag_stub = tag.services.DeviceTagServiceStub(channel)
        req = tag.services.DeviceTagStreamRequest()
        responses = tag_stub.GetAll(req)
        tags = []
        for resp in responses:
            dev_tag = {
                "label": resp.value.key.label.value,
                "value": resp.value.key.value.value,
                "creator_type": resp.value.creator_type,
            }
            tags.append(dev_tag)
    return tags


def get_tags_by_type(creator_type=tag.models.CREATOR_TYPE_USER):
    """Get tags by creator type from CloudVision."""
    with grpc.secure_channel(cvp_url, conn_creds) as channel:
        tag_stub = tag.services.DeviceTagServiceStub(channel)
        req = tag.services.DeviceTagStreamRequest(partial_eq_filter=[tag.models.DeviceTag(creator_type=creator_type)])
        responses = tag_stub.GetAll(req)
        tags = []
        for resp in responses:
            dev_tag = {
                "label": resp.value.key.label.value,
                "value": resp.value.key.value.value,
                "creator_type": resp.value.creator_type,
            }
            tags.append(dev_tag)
    return tags


def get_device_tags(device_id):
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
        tags = []
        for resp in responses:
            dev_tag = {
                "label": resp.value.key.label.value,
                "value": resp.value.key.value.value,
            }
            tags.append(dev_tag)
    return tags


# def create_tag(label: str, value: str):
#     """Create user-defined tag in CloudVision."""
#     tag_url = "/api/resources/tag/v1/DeviceTagConfig"
#     payload = {"key": {"label": label, "value": value}}
#     response = send_request("POST", tag_url, payload)
#     # Skip raising exception if tag already exists
#     if "tag already exists" not in response.text:
#         response.raise_for_status()


# def assign_tag_to_device(device_id: str, label: str, value: str):
#     """Assign user-defined tag to device in CloudVision."""
#     tag_url = "/api/resources/tag/v1/DeviceTagAssignmentConfig"
#     payload = {"key": {"label": label, "value": value, "deviceId": device_id}}
#     response = send_request("POST", tag_url, payload)
#     response.raise_for_status()


def remove_tag_from_device(device_id: str, label: str, value: str):
    """Unassign a tag from a device in CloudVision."""
    with grpc.secure_channel(cvp_url, conn_creds) as channel:
        tag_stub = tag.services.DeviceTagAssignmentConfigServiceStub(channel)
        req = tag.services.DeviceTagAssignmentConfigDeleteRequest(
            key=tag.models.DeviceTagAssignmentKey(
                label=wrappers.StringValue(value=tag_name),
                value=wrappers.StringValue(value=tag_value),
                device_id=wrappers.StringValue(value=device_id),
            )
        )
        tag_stub.Delete(req, timeout=RPC_TIMEOUT)
