"""Test fixtures to be used with unit tests."""
import json


def load_json(path):
    """Load a json file."""
    with open(path, encoding="utf-8") as file:
        return json.loads(file.read())


DEVICE_FIXTURE = load_json("./nautobot_ssot_aristacv/tests/fixtures/get_devices_response.json")
FIXED_INTF_QUERY = load_json("./nautobot_ssot_aristacv/tests/fixtures/get_interfaces_fixed_client_query.json")
INTERFACE_FIXTURE = load_json("./nautobot_ssot_aristacv/tests/fixtures/get_interfaces_fixed_response.json")
