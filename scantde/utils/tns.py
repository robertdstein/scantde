"""
Utility functions for handling TNS names.
"""

def strip_tns_name(name: str) -> str:
    """
    Strip the TNS prefix from a name.

    :param name: The TNS name.
    :return: The stripped name.
    """
    is_digit = [x.isdigit() for x in name]
    idx = is_digit.index(True)
    tns_root = name[idx:].strip()
    return tns_root