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
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # prepare the standard return object
    result = dict(changed=False, check_mode=module.check_mode)

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

    # try a GET request to the API to see what configuration is already there
    get_response = requests.get(
        url,
        headers=headers,
        auth=auth,
        verify=module.params["verify"],
    )

    if get_response.status_code == 404:
        # the VRF does not exist on the device
        configured_vrf = None
        result["existing_config"] = None
    elif get_response.ok:
        # the VRF does exist, so use its configuration
        configured_vrf = get_response.json()
        result["existing_config"] = get_response.json()
    else:
        # any other code means an error, so module should fail
        result["msg"] = f"API request failed with code {get_response.status_code}"
        module.fail_json(**result)

    # prepare the payload to only make the necessary changes
    if configured_vrf == None:
        # need to create the VRF and optionally set the description
        intended_vrf = {
            "Cisco-IOS-XE-native:definition": {"name": f"{module.params['name']}"}
        }

        # only set if it's defined since an empty description
        # is not acceptable by the API
        if module.params["description"]:
            intended_vrf["Cisco-IOS-XE-native:definition"][
                "description"
            ] = f"{module.params['description']}"

        # mark the module as having made changes
        result["intended_config"] = intended_vrf
        result["changed"] = True
    else:
        # the VRF exists but need to check the description
        configured_desc = configured_vrf["Cisco-IOS-XE-native:definition"].get(
            "description"
        )

        # only update if it's defined and different from configured
        if (
            module.params["description"]
            and configured_desc != module.params["description"]
        ):
            # update the description to the new value
            # but preserve any other configuration the VRF may have
            intended_vrf = deepcopy(configured_vrf)
            intended_vrf["Cisco-IOS-XE-native:definition"][
                "description"
            ] = f"{module.params['description']}"

            # mark the module as having made changes
            result["intended_config"] = intended_vrf
            result["changed"] = True

    # send the API request to the device using PUT and only perform changes
    # when a required change has been detected and if check mode is off
    if result["changed"] and not module.check_mode:
        response = requests.put(
            url,
            headers=headers,
            auth=auth,
            verify=module.params["verify"],
            data=json.dumps(intended_vrf),
        )

        # return the JSON response from the API if it exists
        if response.text:
            result["json"] = response.json()

        # add a message based on the status code
        if response.ok:
            result["msg"] = f"OK {response.status_code}"
        # the request failed so the module should fail as well
        else:
            result["msg"] = f"API request failed with code {response.status_code}"
            module.fail_json(**result)

    # return successfully and pass the results to ansible
    module.exit_json(**result)


if __name__ == "__main__":
    main()
