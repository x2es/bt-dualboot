import re
from .convert import mac_from_reg_key, hex_string_from_reg, is_mac_reg_key, int_from_dword_reg, int_from_hex_b_reg 
from bt_dualboot.bluetooth_device import BluetoothDevice

REG_KEY__BLUETOOTH_PAIRING_KEYS = r"ControlSet001\Services\BTHPORT\Parameters\Keys"

def get_device_nodes(from_sections):
    """Extract devices nodes from a section list
    Args:
        from_sections (list[str]): result of 'sections()' function on ...\\Services\\BTHPORT\\Parameters\\Keys section

    Returns:
        list[tuple]: tuple with three elements (adapter mac address, device mac address, section key)
    """
    nodes = [] 
    search_re = r"Services.BTHPORT.Parameters.Keys.([a-f0-9]+)\\([a-f0-9]+)$"
    for sec in from_sections:
        node = re.search(search_re, sec)
        if node is not None:
            nodes.append((mac_from_reg_key(node.groups()[0]), mac_from_reg_key(node.groups()[1]), sec))

    return nodes

def extract_adapter_mac(from_section_key):
    """Extracts adapter MAC from section key
    Args:
        from_section_key (str): kind of 'ControlSet001\\Services\\BTHPORT\\Parameters\\Keys\\d46d6d97629b'

    Returns:
        str: adapter MAC kind of 'D4:6D:6D:97:62:9B'
    """

    res = re.search("Services.BTHPORT.Parameters.Keys.([a-f0-9]+)(.[a-f0-9]+)?$", from_section_key)
    if res is None:
        return None

    return mac_from_reg_key(res.groups()[0])


def get_devices(windows_registry):
    """Returns all BluetoothDevice instances from windows registry
    Args:
        windows_registry (WindowsRegistry): instance used for export data

    Returns:
        list<BluetoothDevice>
            NOTE: If bluetooth < 5.1: filled only `mac`, `adapter_mac` and `pairing_key`
                Else: filled only `mac`, `adapter_mac`, `ltk`, `rand`, `ediv`
    """
    reg_data = windows_registry.export_as_config(REG_KEY__BLUETOOTH_PAIRING_KEYS)
    bluetooth_devices = []

    for section_key in reg_data.keys():
        adapter_mac = extract_adapter_mac(section_key)
        if adapter_mac is None:
            continue

        section = reg_data[section_key]
        for device_mac_raw, pairing_key_raw in section.items():
            if is_mac_reg_key(device_mac_raw):
                bluetooth_devices.append(
                    BluetoothDevice(
                        source=BluetoothDevice.source_windows(),
                        mac=mac_from_reg_key(device_mac_raw),
                        adapter_mac=adapter_mac,
                        pairing_key=hex_string_from_reg(pairing_key_raw),
                    )
                )
    # bluetooth 5.1 devices
    for adapter_mac, device_mac, section_key in get_device_nodes(reg_data.sections()):
        ltk = reg_data.get(section_key, '"ltk"')
        erand = reg_data.get(section_key, '"erand"')
        ediv = reg_data.get(section_key, '"ediv"')
        bluetooth_devices.append(
            BluetoothDevice(
                source=BluetoothDevice.source_windows(),
                mac=device_mac,
                adapter_mac=adapter_mac,
                ltk=hex_string_from_reg(ltk),
                rand=int_from_hex_b_reg(erand),
                ediv=int_from_dword_reg(ediv)
            )
        )

    return bluetooth_devices
