#!/usr/bin/python3

from ansible.module_utils.basic import AnsibleModule
import requests
from requests.auth import HTTPBasicAuth

requests.packages.urllib3.disable_warnings()


def main():

    module_args = dict(
        host=dict(type="str", required=True),
        user=dict(type="str", required=True),
        password=dict(type="str", required=True, no_log=True),
        filter=dict(
            type="str",
            required=False,
            default="all",
            choices=[
                "all",
                "version",
                "memory",
                "platform",
                "hostname",
                "username",
                "vrf",
                "ip",
                "cdp",
                "interface",
                "login",
                "snmp-server",
                "lldp",
            ],
        ),
    )

    module = AnsibleModule(argument_spec=module_args)

    auth = HTTPBasicAuth(module.params["user"], module.params["password"])

    if module.params["filter"] == "all":
        url = f"https://{module.params['host']}/restconf/data/Cisco-IOS-XE-native:native/"
    elif module.params["filter"] == "lldp":
        url = f"https://{module.params['host']}/restconf/data/Cisco-IOS-XE-native:native/Cisco-IOS-XE-lldp:lldp"
    else:
        url = f"https://{module.params['host']}/restconf/data/Cisco-IOS-XE-native:native/{module.params['filter']}"

    headers = {"Accept": "application/yang-data+json"}

    response = requests.get(url, headers=headers, auth=auth, verify=False)

    module.exit_json(changed=False, msg=response.json())


if __name__ == "__main__":
    main()

