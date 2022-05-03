import re


def hex_string_to_pairs(hex_string):
    """Convert hex string to pairs array
    Args:
        hex_string (str): kind of 'D51FFA421C4C'

    Returns:
        list: kind of [D5, 1F, FA, 42, 1C, 4C]
    """
    buf = hex_string
    buf_len = len(buf)

    if buf_len % 2 != 0:
        raise RuntimeError(f"wrong hex string={hex_string}")

    pairs_count = int(buf_len / 2)

    pairs = []
    for i in range(pairs_count):
        start = i * 2
        end = start + 2
        pairs.append(buf[start:end])

    return pairs


def is_mac_reg_key(value):
    """Check is value is valid MAC reg key
    Args:
        value (str): kind of 'd51ffa421c4c' or '"d51ffa421c4c"' or 'MasterIRK' or '"MasterIRK"'

    Returns:
        str: kind of 'D5:1F:FA:42:1C:4C'
    """

    return re.match("^[a-f0-9]{12}$", _unquote(value)) is not None


def mac_from_reg_key(mac_key):
    """Convert device MAC from Windows registry key format to regular
    Args:
        mac_key (str): kind of 'd51ffa421c4c' or '"d51ffa421c4c"'

    Returns:
        str: kind of 'D5:1F:FA:42:1C:4C'
    """

    return ":".join(hex_string_to_pairs(_unquote(mac_key).upper()))


def mac_to_reg_key(mac):
    """Convert device MAC to Windows registry key format
    Args:
        mac (str): kind of 'D5:1F:FA:42:1C:4C'

    Returns:
        str: kind of 'd51ffa421c4c'
    """

    return "".join(mac.split(":")).lower()


def hex_string_from_reg(hex_string_reg):
    """Convert hex string from Windows registry format
    Args:
        hex_string_reg (str): kind of 'hex:a6,1b,7f,1b,d9,a3,5f,3c,f7,e6,75,ef,21,61,a8,36'

    Returns:
        str: kind of 'A61B7F1BD9A35F3CF7E675EF2161A836'
    """

    _, value = hex_string_reg.split(":")
    return "".join(value.split(",")).upper()


def hex_string_to_reg_value(hex_string):
    """Convert hex string to Windows registry value
    Args:
        hex_string_reg (str): kind of 'A61B7F1BD9A35F3CF7E675EF2161A836'

    Returns:
        str: kind of 'hex:a6,1b,7f,1b,d9,a3,5f,3c,f7,e6,75,ef,21,61,a8,36'
    """

    value = ",".join(hex_string_to_pairs(hex_string.lower()))
    return f"hex:{value}"


def _unquote(value):
    """unquote value is quoted
    Args:
        value (str): kind of 'd51ffa421c4c' or '"d51ffa421c4c"'

    Returns:
        str: kind of 'd51ffa421c4c'
    """
    if value[0] == '"' and value[-1] == '"':
        return value[1:-1]

    return value
