from ansible import errors


class FilterModule:
    """Defines a filter module object."""

    @staticmethod
    def filters():
        """Returns the Ansible filter bindings dictionary."""
        return {
            "verify_intended_state": FilterModule.verify_intended_state,
        }

    @staticmethod
    def verify_intended_state(operational, intended):
        """Returns a pass/fail comparison of intended and operational state.

        Compares NXOS (operational) state (from the show int brief command)
        to a provided list of interface and state mappings (intended)

        SAMPLE intended
        [
            {
                "name": "Ethernet1/1",
                "state": "up"
            },
            {
                "name": "mgmt0",
                "state": "up"
            },
        ]

        SAMPLE operational
        {
            "TABLE_interface": {
                "ROW_interface": [
                    {
                        "interface": "mgmt0",
                        "state": "up",
                        "ip_addr": "10.0.0.15",
                        "speed": "1000",
                        "mtu": "1500"
                    },
                    {
                        "interface": "Ethernet1/1",
                        "vlan": "1",
                        "type": "eth",
                        "portmode": "access",
                        "state": "up",
                        "state_rsn_desc": "none",
                        "speed": "1000",
                        "ratemode": "D"
                    },
                ]
            }
        }


        Args:
            operational (dict): the output of `show int brief | json`
            intended (list): a list of interfaces and their states

        Returns:
            dict: A dictionary containing the lists of interfaces that
                  passed and failed verification
        """
        # First prepare the data coming from NXOS for ease of lookup
        # Change from a list of interface dictionaries to a dictionary
        # keyed on the interface name
        oper_keyed = {}
        for oper_intf in operational["TABLE_interface"]["ROW_interface"]:
            oper_keyed[oper_intf["interface"]] = oper_intf

        pass_list = []
        fail_list = []
        # This is a list of name/state pairs describing the intended state
        # of a bunch of interfaces (not necessarily the same set).
        for interface in intended:
            # Look for the interface name in the operational dictionary
            # as an exact match only - with UNKNOWN as a safe default
            oper_intf = oper_keyed.get(interface["name"])
            if oper_intf:
                oper_state = oper_intf.get("state", "UNKNOWN")
            else:
                oper_state = "UNKNOWN"

            # Compare operational to intended
            if oper_state != interface["state"]:
                fail_list.append(interface["name"])
            else:
                pass_list.append(interface["name"])

        # Return a dictionary with two keys containing the lists for easy
        # subsequent parsing
        return {"pass": pass_list, "fail": fail_list}
