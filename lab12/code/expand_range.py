import re
from ansible import errors


class FilterModule:
    """Defines a filter module object."""

    @staticmethod
    def filters():
        """Returns the Ansible filter bindings dictionary."""
        return {
            "expand_range": FilterModule.expand_range,
        }

    @staticmethod
    def expand_range(text):
        """Expands a range specifier for interface to a list."""
        # Look for at least one non-whitespace character for the base
        # followed by a range spec: [x:y] where x and y are integers
        result = re.findall(r"^(\S+)(\[\d+:\d+\])$", text)

        # Check if we have a valid match
        # "Loopback100[1:3]" yields [('Loopback100', '[1:3]')]
        # but "Loopback100" yields []
        if result:
            # Process the range spec '[1:3]' into start and stop as strings
            start, stop = result[0][1].strip("[]").split(":")
            # Generate the expanded list by appending numbers to the
            # base string from the provided range
            base = result[0][0]
            expanded_list = []
            for i in range(int(start), int(stop) + 1):
                expanded_list.append(f"{base}{i}")

            return expanded_list

        # No range provided or no match at all, so raise an error
        raise errors.AnsibleFilterError(
            f"expand_range filter error: No valid range found in '{text}'!"
        )
