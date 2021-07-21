"""Script for loading base data for plugin testing."""
from dataclasses import dataclass
from typing import Any

import pynautobot


def get_or_create(object_endpoint, search_key, search_term, **kwargs):
    """Get or create object with pynautobot.
    Args:
        object_endpoint (pynautobot Endpoint): Endpoint to make get and post requests to
        search_key (str): Key to use within the get request, such as name or model
        search_term (str): What is being searched for
    Returns:
        obj (pynautobot object), created (bool): Object being created, and whether or not it was created
    """
    created = False
    search = {search_key: search_term}
    if kwargs.get("just_create_device"):
        try:
            print("Just creating device")
            obj = object_endpoint.create(**search, **kwargs)
            created = True
            return obj, created
        except:  # pylint: disable=bare-except # noqa: E722, E261
            return None, True

    obj = object_endpoint.get(**search)
    if obj is None:
        obj = object_endpoint.create(**search, **kwargs)
        created = True

    return obj, created


@dataclass
class Role:
    name: str
    color: str
    obj: Any


def main():
    # Developed for use with local dev instance and sample cred file. Change token if needed.
    nautobot = pynautobot.api(url="http://localhost:8080", token="0123456789abcdef0123456789abcdef01234567")  # nosec
    site, created = get_or_create(nautobot.dcim.sites, "name", "Lab", slug="lab", status="active")
    print(site, created)

    roles = [Role("Spine", "2196f3", None), Role("Leaf", "9e9e9e", None)]
    for role in roles:
        role_obj, created = get_or_create(
            nautobot.dcim.device_roles, "name", role.name, slug=role.name.lower(), color=role.color, vm_role=False
        )
        role.obj = role_obj
        print(role, created)

    manufacturer, created = get_or_create(nautobot.dcim.manufacturers, "name", "Arista", slug="arista")
    manufacturer2, created2 = get_or_create(nautobot.dcim.manufacturers, "name", "Cisco", slug="cisco")
    print(manufacturer, created)

    device_type, created = get_or_create(
        nautobot.dcim.device_types, "model", "vEOS", slug="veos", manufacturer=manufacturer.id
    )
    device_type2, created2 = get_or_create(
        nautobot.dcim.device_types, "model", "IOS", slug="ios", manufacturer=manufacturer2.id
    )
    print(device_type, created)

    platform, created = get_or_create(nautobot.dcim.platforms, "name", "EOS", slug="eos", manufacturer=manufacturer.id)
    print(platform, created)

    devices = [("eos-leaf1", "leaf"), ("eos-leaf2", "leaf"), ("eos-spine1", "spine"), ("eos-spine2", "spine")]
    for device in devices:
        # Set role id
        role_id = roles[0].obj.id if device[1] == "spine" else roles[1].obj.id
        device_obj, created = get_or_create(
            nautobot.dcim.devices,
            "name",
            device[0],
            slug=device[0].lower(),
            device_role=role_id,
            device_type=device_type.id,
            site=site.id,
            platform=platform.id,
            status="active",
        )
        print(device_obj, created)


if __name__ == "__main__":
    main()
