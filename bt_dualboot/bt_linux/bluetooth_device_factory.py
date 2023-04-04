from bt_dualboot.bluetooth_device import BluetoothDevice
import re
from configparser import ConfigParser


def extract_macs(device_info_path):
    """Extracts adapter and device MAC from path to /info file

    Args:
        device_info_path (str): Kind of .../foo/A4:6B:6C:9D:E2:FB/B6:C2:D3:E5:F2:0D/info

    Returns:
        hash: Kind of { device_mac: <device MAC>, adapter_mac: <adapter MAC> }
    """

    match = re.search("([A-F0-9:]+)/([A-F0-9:]+)/info$", device_info_path)
    if match is None:
        return None

    adapter_mac, device_mac = match.groups()
    return {"device_mac": device_mac, "adapter_mac": adapter_mac}


def extract_info(device_info_path):
    """Extracts adapter info from Linux /path/to/info

    Args:
        device_info_path (str): Kind of .../foo/A4:6B:6C:9D:E2:FB/B6:C2:D3:E5:F2:0D/info

    Returns:
        hash: Kind of { name:, class:, pairing_key: , long_term_key:, ediv:, rand:}
    """
    config = ConfigParser()
    config.read(device_info_path)
    link_key = config.get("LinkKey", "Key", fallback=None)
    long_term_key = config.get("LongTermKey", "Key", fallback=None)
    ediv = config.get("LongTermKey", "EDiv", fallback=None)
    rand = config.get("LongTermKey", "Rand", fallback=None)

    if not link_key and not long_term_key:
        raise KeyError("Neither LinkKey->Key nor LongTermKey->Key exist")
    # fmt: off
    return {
        "name":         config.get("General", "Name"),
        "class":        config.get("General", "Class", fallback=None),
        "pairing_key":  link_key,
        "long_term_key": long_term_key,
        "ediv": ediv,
        "rand": rand
    }
    # fmt: on


def bluetooth_device_factory(device_info_path):
    """Build BluetoothDevice instance for given /path/to/info

    Args:
        device_info_path (str): Kind of .../foo/A4:6B:6C:9D:E2:FB/B6:C2:D3:E5:F2:0D/info

    Returns:
        BluetoothDevice
    """

    macs = extract_macs(device_info_path)
    info = extract_info(device_info_path)

    return BluetoothDevice(
        source=BluetoothDevice.source_linux(),
        device_class=info["class"],
        mac=macs["device_mac"],
        name=info["name"],
        pairing_key=info["pairing_key"],
        adapter_mac=macs["adapter_mac"],
        ltk=info["long_term_key"],
        ediv=int(info["ediv"]) if info["ediv"] else None,
        rand=int(info["rand"]) if info["rand"] else None
    )
