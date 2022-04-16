from pytest import fixture

#
# EPERIMENTAL:
#   this module
#       * includes fixtures from foreign module
#       * shares fixtures for other foreign modules
#
from tests.windows_registry.shared_fixtures import *

from bt_windows.convert import *

"""
Initializes and chekcs following test set.

    2 BT adapters:
        A (A4:6B:6C:9D:E2:FB):
            4 BT devices,
                2 synced     with Windows               (pairing_keys the same)
                    A4:BF:C6:D0:E5:FF
                    B6:C2:D3:E5:F2:0D

                1 not synced with Windows               (pairing_keys differ)
                    C2:9E:1D:E2:3D:A5

                1 not paired in Windows                 (abset in Windows registry)
                    D1:8A:4E:71:5D:C1

                1 paired in Windows but not in Linux    (eixst in Windows registry)
                    E9:1D:FE:2A:C3:C8

        B (B4:6B:6C:9D:E2:FB):
            3 BT devices
                1 synced     with Windows
                    A4:80:1D:C5:4F:7E

                1 not synced with Windows
                    B8:94:A5:FD:F1:0A

                1 not paired in Windows
                    C4:72:B3:6F:82:42
"""


@fixture
def test_scheme():
    return {
        # adapter MAC
        "A4:6B:6C:9D:E2:FB": {
            # device MAC:        pairing_key                            NOTE
            # -----------        -----------                            ----
            "A4:BF:C6:D0:E5:FF": "A43C6BD9E1592C1FFA0DE17F3DB6F38B",  # same
            "B6:C2:D3:E5:F2:0D": "A515CBE4E8F2E236FF999C0A53369EF6",  # same
            "C2:9E:1D:E2:3D:A5": "12121212121212121212121212121212",  # differ
            # absent 'D1:8A:4E:71:5D:C1'
            "E9:1D:FE:2A:C3:C8": "34343434343434343434343434343434",  # not paired in linux
        },
        "B4:6B:6C:9D:E2:FB": {
            "A4:80:1D:C5:4F:7E": "A12B5D441EC1A9D517794FC2B4889202",  # same
            "B8:94:A5:FD:F1:0A": "71717171717171717171717171717171",  # differ
            # absent 'C4:72:B3:6F:82:42'
        },
    }


@fixture
def import_devices(windows_registry, test_scheme):
    for_import = {}

    for adapter_mac, devices in test_scheme.items():
        # SAMPLE: PREFIX\ControlSet001\Services\BTHPORT\Parameters\Keys\d46d6d97629b
        reg_section = wp(
            r"ControlSet001\Services\BTHPORT\Parameters\Keys" + "\\" + mac_to_reg_key(adapter_mac)
        )
        for_import[reg_section] = {}

        for device_mac, pairing_key in devices.items():
            for_import[reg_section][
                f'"{mac_to_reg_key(device_mac)}"'
            ] = hex_string_to_reg_value(pairing_key)  # fmt: skip

    windows_registry.import_dict(for_import, safe=False)
