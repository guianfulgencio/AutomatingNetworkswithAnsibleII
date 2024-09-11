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
sent_payload:
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
    url = f"{base_url}/Cisco-IOS-XE-native:vrf/definition={module.params['name']}"

    # build PATCH request payload
    payload = {"Cisco-IOS-XE-native:definition": {"name": f"{module.params['name']}"}}

    # only set if it's defined since an empty description is not acceptable by the API
    if module.params["description"]:
        payload["Cisco-IOS-XE-native:definition"][
            "description"
        ] = f"{module.params['description']}"

    # add this to the module output for easier troubleshooting
    result["sent_payload"] = payload

    # send the API request to the device (PATCH)
    response = requests.patch(
        url,
        data=json.dumps(payload),
        headers=headers,
        auth=auth,
        verify=module.params["verify"],
    )

    # return the json response from the API if it exists
    if response.text:
        result["json"] = response.json()

    # since it's a blind PATCH request, always assume a change was made
    if response.ok:
        result["changed"] = True
        result["msg"] = f"OK {response.status_code}"
    # the request failed so the module should fail as well
    else:
        result["msg"] = f"API request failed with code {response.status_code}"
        module.fail_json(**result)

    # return successfully and pass the results to ansible
    module.exit_json(**result)


if __name__ == "__main__":
    main()

