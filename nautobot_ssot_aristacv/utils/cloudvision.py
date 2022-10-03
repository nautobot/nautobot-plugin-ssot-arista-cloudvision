"""Utility functions for CloudVision Resource API."""
import ssl

import grpc
from pprint import pprint as pretty_print
import requests
from arista.inventory.v1 import models, services
from arista.tag.v1 import models as tag_models
from arista.tag.v1 import services as tag_services
from django.conf import settings
from google.protobuf.wrappers_pb2 import StringValue  # pylint: disable=no-name-in-module

from cloudvision.Connector.grpc_client import GRPCClient, create_query
from cloudvision.Connector.codec.custom_types import FrozenDict
from cloudvision.Connector.codec import Wildcard, Path

RPC_TIMEOUT = 30

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG["nautobot_ssot_aristacv"]


class AuthFailure(Exception):
    """Exception raised when authenticating to on-prem CVP fails."""

    def __init__(self, error_code, message):
        """Populate exception information."""
        self.expression = error_code
        self.message = message
        super().__init__(self.message)


class CloudvisionApi:  # pylint: disable=too-many-instance-attributes, too-many-arguments
    """Arista Cloudvision Api."""

    def __init__(
        self,
        cvp_host: str,
        cvp_port: str = None,
        verify: bool = True,
        username: str = None,
        password: str = None,
        cvp_token: str = None,
    ):
        """Create Cloudvision API connection."""
        self.comm_channel = None
        self.cvp_host = cvp_host
        self.cvp_port = cvp_port
        self.cvp_url = f"{cvp_host}:{cvp_port}"
        self.verify = verify
        self.username = username
        self.password = password
        self.cvp_token = cvp_token
        self.cvp_cert = None

        self.connect()

    def connect(self):
        """Connect shared gRPC channel to the configured CloudVision instance."""
        # If CVP_HOST is defined, we assume an on-prem installation.
        if self.cvp_host:
            # If we don't want to verify the cert, it will be downloaded from the server and automatically trusted for gRPC.
            if self.verify:
                # Otherwise, the server is expected to have a valid certificate signed by a well-known CA.
                channel_creds = grpc.ssl_channel_credentials()
            else:
                self.cvp_cert = ssl.get_server_certificate((self.cvp_host, int(self.cvp_port)))
                channel_creds = grpc.ssl_channel_credentials(bytes(self.cvp_cert, "utf-8"))
            if self.cvp_token:
                call_creds = grpc.access_token_call_credentials(self.cvp_token)
            elif self.username != "" and self.password != "":  # nosec
                response = requests.post(
                    f"https://{self.cvp_host}/cvpservice/login/authenticate.do",
                    auth=(self.username, self.password),
                    verify=self.verify,
                )
                session_id = response.json().get("sessionId")
                if not session_id:
                    error_code = response.json().get("errorCode")
                    error_message = response.json().get("errorMessage")
                    raise AuthFailure(error_code, error_message)
                elif self.cvp_token is None:
                    self.cvp_token = session_id
                call_creds = grpc.access_token_call_credentials(session_id)
            else:
                raise AuthFailure(
                    error_code="Missing Credentials", message="Unable to authenticate due to missing credentials."
                )
        # Set up credentials for CVaaS using supplied token.
        else:
            self.cvp_url = PLUGIN_SETTINGS.get("cvaas_url", "www.arista.io:443")
            call_creds = grpc.access_token_call_credentials(self.cvp_token)
            channel_creds = grpc.ssl_channel_credentials()
        conn_creds = grpc.composite_channel_credentials(channel_creds, call_creds)
        self.comm_channel = grpc.secure_channel(self.cvp_url, conn_creds)

    def disconnect(self):
        """Close the shared gRPC channel."""
        self.comm_channel.close()

    def get_devices(self):
        """Get active devices from CloudVision inventory."""
        device_stub = services.DeviceServiceStub(self.comm_channel)
        if PLUGIN_SETTINGS.get("import_active"):
            req = services.DeviceStreamRequest(
                partial_eq_filter=[models.Device(streaming_status=models.STREAMING_STATUS_ACTIVE)]
            )
        else:
            req = services.DeviceStreamRequest()
        responses = device_stub.GetAll(req)
        devices = []
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

    def get_device_id(self, device_name: str):
        """Get device_id for device_name from CloudVision inventory."""
        device_stub = services.DeviceServiceStub(self.comm_channel)
        req = services.DeviceStreamRequest(
            partial_eq_filter=[models.Device(hostname=device_name, streaming_status=models.STREAMING_STATUS_ACTIVE)]
        )
        resp = device_stub.GetOne(req)
        return resp.value.key.device_id.value

    def get_tags(self):
        """Get all tags from CloudVision."""
        tag_stub = tag_services.DeviceTagServiceStub(self.comm_channel)
        req = tag_services.DeviceTagStreamRequest()
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

    def get_tags_by_type(self, creator_type: int = tag_models.CREATOR_TYPE_USER):
        """Get tags by creator type from CloudVision."""
        tag_stub = tag_services.DeviceTagServiceStub(self.comm_channel)
        req = tag_services.DeviceTagStreamRequest(partial_eq_filter=[tag_models.DeviceTag(creator_type=creator_type)])
        responses = tag_stub.GetAll(req)
        tags = []
        for resp in responses:
            dev_tag = {
                "label": resp.value.key.label.value,
                "value": resp.value.key.value.value,
            }
            tags.append(dev_tag)
        return tags

    def get_device_tags(self, device_id: str):
        """Get tags for specific device."""
        tag_stub = tag_services.DeviceTagAssignmentConfigServiceStub(self.comm_channel)
        req = tag_services.DeviceTagAssignmentConfigStreamRequest(
            partial_eq_filter=[
                tag_models.DeviceTagAssignmentConfig(
                    key=tag_models.DeviceTagAssignmentKey(
                        device_id=StringValue(value=device_id),
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

    def create_tag(self, label: str, value: str):
        """Create user-defined tag in CloudVision."""
        tag_stub = tag_services.DeviceTagConfigServiceStub(self.comm_channel)
        req = tag_services.DeviceTagConfigSetRequest(
            value=tag_models.DeviceTagConfig(
                key=tag_models.TagKey(label=StringValue(value=label), value=StringValue(value=value))
            )
        )
        try:
            tag_stub.Set(req)
        except grpc.RpcError as err:
            # Ignore RPC error if tag already exists for idempotency
            print(f"Failure to create tag: {err}")
            raise err

    def delete_tag(self, label: str, value: str):
        """Delete user-defined tag in CloudVision."""
        tag_stub = tag_services.DeviceTagConfigServiceStub(self.comm_channel)
        req = tag_services.DeviceTagConfigDeleteRequest(
            key=tag_models.TagKey(label=StringValue(value=label), value=StringValue(value=value))
        )
        try:
            tag_stub.Delete(req)
        # Skip error of tags that may be assigned to devices manually in CloudVision
        except grpc.RpcError as err:
            print(f"Failure to delete tag: {err}")
            raise err

    def assign_tag_to_device(self, device_id: str, label: str, value: str):
        """Assign user-defined tag to device in CloudVision."""
        tag_stub = tag_services.DeviceTagAssignmentConfigServiceStub(self.comm_channel)
        req = tag_services.DeviceTagAssignmentConfigSetRequest(
            value=tag_models.DeviceTagAssignmentConfig(
                key=tag_models.DeviceTagAssignmentKey(
                    label=StringValue(value=label),
                    value=StringValue(value=value),
                    device_id=StringValue(value=device_id),
                )
            )
        )
        tag_stub.Set(req)

    def remove_tag_from_device(self, device_id: str, label: str, value: str):
        """Unassign a tag from a device in CloudVision."""
        tag_stub = tag_services.DeviceTagAssignmentConfigServiceStub(self.comm_channel)
        req = tag_services.DeviceTagAssignmentConfigDeleteRequest(
            key=tag_models.DeviceTagAssignmentKey(
                label=StringValue(value=label),
                value=StringValue(value=value),
                device_id=StringValue(value=device_id),
            )
        )
        tag_stub.Delete(req, timeout=RPC_TIMEOUT)

    # This section is based off example code from Arista: https://github.com/aristanetworks/cloudvision-python/blob/trunk/examples/Connector/get_intf_status.py

    @staticmethod
    def get_query(client, dataset, pathElts):
        """Returns a query on a path element.

        Args:
            client (obj): GRPC client connection.
            dataset (dict): Data related to query.
            pathElts (List[str]): List of strings denoting path elements for query.

        Returns:
            _type_: _description_
        """
        result = {}
        query = [create_query([(pathElts, [])], dataset)]

        for batch in client.get(query):
            for notif in batch["notifications"]:
                if debug:
                    pretty_print(notif["updates"])
                result.update(notif["updates"])
        return result

    def unfreeze_frozen_dict(self, frozen_dict):
        """Used to unfreeze Frozen dictionaries.

        Args:
            frozen_dict (FrozenDict|dict|str): Potentially frozen dict to be unfrozen.

        Returns:
            dict|str|list: Unfrozen contents of FrozenDict that was passed in.
        """
        if isinstance(frozen_dict, (dict, FrozenDict)):
            return dict({k: self.unfreeze_frozen_dict(v) for k, v in frozen_dict.items()})

        if isinstance(frozen_dict, (str)):
            return frozen_dict

        try:
            return [self.unfreeze_frozen_dict(i) for i in frozen_dict]
        except TypeError:
            pass

        return frozen_dict

    def get_device_type(self, client, dId):
        """Returns the type of the device: modular/fixed.

        Args:
            client (GRPCClient): GRPCClient connection.
            dId (str): Device ID to determine type for.

        Returns:
            str: Type of device, either modular or fixed.
        """
        pathElts = ["Sysdb", "hardware", "entmib"]
        query = self.get_query(client, dId, pathElts)
        query = self.unfreeze_frozen_dict(query)
        if query["fixedSystem"] is None:
            dType = "modular"
        else:
            dType = "fixedSystem"
        return dType

    @staticmethod
    def printIntfStatus(intfStatus: list, deviceId: str):
        """Helper function to print the interface statuses.

        Args:
            intfStatus (list): List of dictionaries the status of all interfaces on device.
        """
        print(f"{'Interface Name':<25}{'status'}\n")
        connected = 0
        down = 0
        for interface in intfStatus:
            print(f"{interface['interface']:<25}{interface['status']}")
            if interface["active"] is True:
                if interface["status"] == "linkUp":
                    connected += 1
                else:
                    down += 1
        print(f"\nEthernet Status on {deviceId}:")
        print(f"{connected:>10} interfaces connected (including Management)")
        print(f"{down:>10} interfaces down")

    def getIntfStatusChassis(self, client, dId):
        """Returns the interfaces report for a modular device.

        Args:
            client (_type_): _description_
            dId (_type_): _description_
        """
        # Fetch the list of slices/linecards
        pathElts = ["Sysdb", "interface", "status", "eth", "phy", "slice"]
        dataset = dId
        query = self.get_query(client, dataset, pathElts)
        queryLC = self.unfreeze_frozen_dict(query).keys()
        intfStatusChassis = []

        # Go through each linecard and get the state of all interfaces
        for lc in queryLC:
            pathElts = ["Sysdb", "interface", "status", "eth", "phy", "slice", lc, "intfStatus", Wildcard()]

            query = [create_query([(pathElts, [])], dataset)]

            for batch in client.get(query):
                for notif in batch["notifications"]:
                    intfStatusChassis.append(
                        {
                            "interface": notif["path_elements"][-1],
                            "status": notif["updates"]["linkStatus"]["Name"],
                            "active": notif["updates"]["active"],
                        }
                    )
        self.printIntfStatus(intfStatusChassis, dId)

    def getIntfStatusFixed(self, client, dId):
        """Returns the interfaces report for a fixed system device.

        Args:
            client (_type_): _description_
            dId (_type_): _description_
        """
        pathElts = ["Sysdb", "interface", "status", "eth", "phy", "slice", "1", "intfStatus", Wildcard()]
        query = [create_query([(pathElts, [])], dId)]
        query = self.unfreeze_frozen_dict(query)

        intfStatusFixed = []
        for batch in client.get(query):
            for notif in batch["notifications"]:
                try:
                    intfStatusFixed.append(
                        {
                            "interface": notif["path_elements"][-1],
                            "status": notif["updates"]["linkStatus"]["Name"],
                            "active": notif["updates"]["active"],
                        }
                    )
                except KeyError as e:
                    print(e)
                    continue
        self.printIntfStatus(intfStatusFixed, dId)

    def get_interface_status(self, dId):

        with GRPCClient(self.cvp_url, tokenValue=self.cvp_token, key=None, ca=None, certsValue=self.cvp_cert) as client:
            entmibType = self.get_device_type(client, dId)
            if entmibType == "modular":
                self.getIntfStatusChassis(client, dId)
            else:
                self.getIntfStatusFixed(client, dId)

        return 0
