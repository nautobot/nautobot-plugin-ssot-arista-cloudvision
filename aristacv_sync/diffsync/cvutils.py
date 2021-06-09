"""Utility functions for CloudVision Resource API."""
import os
import json

import requests

CVP_URL = "https://www.arista.io"
TOKEN = os.environ["CVP_TOKEN"]


def get_devices():
    """Get devices from inventory."""
    device_url = "/api/resources/inventory/v1/Device/all"
    url = CVP_URL + device_url
    head = {"Authorization": "Bearer {}".format(TOKEN)}
    response = requests.get(url, headers=head)
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
    url = CVP_URL + device_tag_url
    head = {"Authorization": "Bearer {}".format(TOKEN)}
    payload = {
        "partialEqFilter": [{"key": {"deviceId": device_id, "interfaceId": if_id, "label": label, "value": value}}]
    }
    response = requests.get(url, headers=head, json=payload)
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
    url = CVP_URL + tag_url
    head = {"Authorization": "Bearer {}".format(TOKEN)}
    response = requests.post(url, headers=head, json=payload)
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
