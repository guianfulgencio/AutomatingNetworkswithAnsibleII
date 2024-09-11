#!/usr/bin/env python3

DOCUMENTATION = """
---
module: iosxe_rest_vrf
short_description: This module updates VRF configuration via the IOSXE REST API.
version_added: "1.0.0"
description: This module uses the requests Python library to make API calls against the IOSXE device.
options:
    host:
        description: Enter the IP or hostname of the IOSXE device
        required: true
        type: str
    user:
        description: Enter the device username
        required: true
        type: str
    password:
        description: Enter the device password
        required: true
        type: str
    verify:
        description: Enable or disable SSL verification, it will disabled by default
        required: false
        type: bool
    name:
        description: The VRF's name you want to manage
        required: true
        type: str
    description:
        description: The VRF's description (optional)
        required: false
        type: str

author:
    - NetworkToCode (@networktocode)
"""

EXAMPLES = """
# Collect Device Version
- name: UPDATE VRF DESCRIPTION
  iosxe_rest_vrf:
    host: "{{ inventory_hostname }}"
    user: "{{ username }}"
    password: "{{ password }}"
    name: CORP
    description: VRF FOR CORPORATE USERS
"""

RETURN = """
# These are examples of possible return values, and in general should use other names for return values.
intended_config:
    description: The VRF data that will be sent to the API via the PATCH request
    type: str
    returned: always
    sample: '{"Cisco-IOS-XE-native:definition": {"description": "VRF FOR CORPORATE USERS", "name": "CORP"}}}'
msg:
    description: A status message including the HTTP response code.
    type: str
    returned: always
    sample: 'OK 204'
"""

from ansible.module_utils.basic import AnsibleModule
from copy import deepcopy
import requests
import json

requests.packages.urllib3.disable_warnings()


def main():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        host=dict(type="str", required=True),
        user=dict(type="str", required=True),
        password=dict(type="str", required=True, no_log=True),
        verify=dict(type="bool", default=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
    )
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    # prepare the standard return object
    result = dict(changed=False)

    # set up the API request parameters
    auth = requests.auth.HTTPBasicAuth(module.params["user"], module.params["password"])
    # this module supports only json
    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json",
    }
    # this module supports only the Cisco-IOS-XE-native data model
    base_url = (
        f"https://{module.params['host']}/restconf/data/Cisco-IOS-XE-native:native"
    )
    # manages vrf by name
    url = f"{base_url}/vrf/definition={module.params['name']}"

    ##########################################
    # NEW CODE WITH IDEMPOTENT LOGIC GOES HERE
    ##########################################

    # return successfully and pass the results to ansible
    module.exit_json(**result)


if __name__ == "__main__":
    main()
