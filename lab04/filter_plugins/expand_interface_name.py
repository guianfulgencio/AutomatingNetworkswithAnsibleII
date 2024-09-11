from ansible import errors

INTERFACE_MAPPING = {
    "as": "Async",
    "br": "Bridge",
    "di": "Dialer",
    "et": "Ethernet",
    "fa": "FastEthernet",
    "fo": "FortyGigabitEthernet",
    "gi": "GigabitEthernet",
    "lo": "Loopback",
    "mg": "Mgmt",
    "po": "Port-Channel",
    "se": "Serial",
    "te": "TenGigabitEthernet",
    "tu": "Tunnel",
    "vl": "Vlan",
    "vx": "Vxlan",
}


class FilterModule:
    """Defines a filter module object."""

    @staticmethod
    def filters():
        """Returns the Ansible filter bindings dictionary."""
        return {
            "expand_interface_name": FilterModule.expand_interface_name,
            "expand_interface_names": FilterModule.expand_interface_names,
        }

    @staticmethod
    def expand_interface_name(interface_name):
        """Expands abbreviated interface names."""
        return INTERFACE_MAPPING.get(
            interface_name.strip().lower()[0:2], interface_name
        )

    @staticmethod
    def expand_interface_names(interface_names):
        """Expands abbreviated interface names."""
        if isinstance(interface_names, str):
            # Same as previously, it's just one interface name
            return INTERFACE_MAPPING.get(
                interface_names.strip().lower()[0:2], interface_names
            )
        elif isinstance(interface_names, list):
            expanded_names = []
            for name in interface_names:
                long_name = INTERFACE_MAPPING.get(name.strip().lower()[0:2], name)
                expanded_names.append(long_name)
            return expanded_names
        else:
            raise errors.AnsibleFilterError(
                "expand_interface_names filter error: provide a string or a list of strings!"
            )
