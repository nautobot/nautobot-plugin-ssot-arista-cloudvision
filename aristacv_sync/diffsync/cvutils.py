"""Utility functions for CloudVision Resource API."""
import os
import json

import requests

CVP_URL = "https://www.arista.io"
TOKEN = os.environ["CVP_TOKEN"]


def send_request(method, url, payload=None):
    """Send requests to CloudVision URL using method and payload provided."""
    header = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.request(method, CVP_URL + url, headers=header, json=payload)
    return response


def get_devices():
    """Get devices from inventory."""
    device_url = "/api/resources/inventory/v1/Device/all"
    response = send_request("GET", device_url)
    devices = []
    response.raise_for_status()
    for line in response.text.split():
        temp = json.loads(line)
        # Only add active devices
        if temp["result"]["value"]["streamingStatus"] == "STREAMING_STATUS_ACTIVE":
            device = {
                "device_id": temp["result"]["value"]["key"]["deviceId"],
                "hostname": temp["result"]["value"]["hostname"],
                "fqdn": temp["result"]["value"]["fqdn"],
                "sw_ver": temp["result"]["value"]["softwareVersion"],
                "model": temp["result"]["value"]["modelName"],
            }
            devices.append(device)
    return devices


def get_device_tags(device_id=None, if_id=None, label=None, value=None):
    """Get device tags with optional filter."""
    device_tag_url = "/api/resources/tag/v1/DeviceTag/all"
    payload = {
        "partialEqFilter": [{"key": {"deviceId": device_id, "interfaceId": if_id, "label": label, "value": value}}]
    }
    response = send_request("GET", device_tag_url, payload)
    response.raise_for_status()
    tags = []
    for line in response.text.split():
        temp = json.loads(line)
        tag = {
            "label": temp["result"]["value"]["key"]["label"],
            "value": temp["result"]["value"]["key"]["value"],
            "type": temp["result"]["value"]["creatorType"],
        }
        tags.append(tag)
    return tags


def get_interface_tags(device_id=None, if_id=None, label=None, value=None):
    """Get interface tag with optional filter."""
    tag_url = "/api/resources/tag/v1/InterfaceTagAssignmentConfig/all"
    payload = {
        "partialEqFilter": [{"key": {"deviceId": device_id, "interfaceId": if_id, "label": label, "value": value}}]
    }
    response = send_request("POST", tag_url, payload)
    response.raise_for_status()
    tags = []
    for line in response.text.split():
        temp = json.loads(line)
        tag = {
            "label": temp["result"]["value"]["key"]["label"],
            "value": temp["result"]["value"]["key"]["value"],
        }
        tags.append(tag)
    return tags


def create_tag(label: str, value: str):
    """Create user-defined tag in CloudVision."""
    tag_url = "/api/resources/tag/v1/DeviceTagConfig"
    payload = {"key": {"label": label, "value": value}}
    response = send_request("POST", tag_url, payload)
    # Skip raising exception if tag already exists
    if "tag already exists" not in response.text:
        response.raise_for_status()


def assign_tag_to_device(device_id: str, label: str, value: str):
    """Assign user-defined tag to device in CloudVision."""
    tag_url = "/api/resources/tag/v1/DeviceTagAssignmentConfig"
    payload = {"key": {"label": label, "value": value, "deviceId": device_id}}
    response = send_request("POST", tag_url, payload)
    response.raise_for_status()
