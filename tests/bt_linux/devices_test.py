from unittest.mock import patch
import os

from .shared_fixtures import *
from bt_linux.devices import *


@patch("bt_linux.devices.LINUX_BT_DIR", bt_linux_sample_01_unwrapped())
class TestDevices:
    def test_get_adapters_macs(self):
        expected = ["A4:6B:6C:9D:E2:FB", "B4:6B:6C:9D:E2:FB"]
        adapters = get_adapters_macs()
        assert sorted(adapters) == sorted(expected)

    def test_get_adapters_paths(self, bt_linux_sample_01):
        expected = [
            os.path.join(bt_linux_sample_01, mac)
            for mac in ["A4:6B:6C:9D:E2:FB", "B4:6B:6C:9D:E2:FB"]
        ]
        adapters = get_adapters_paths()
        assert sorted(adapters) == sorted(expected)

    def test_get_devices_paths(self, bt_linux_sample_01):
        sample_list = [
            "A4:6B:6C:9D:E2:FB/A4:BF:C6:D0:E5:FF",
            "A4:6B:6C:9D:E2:FB/B6:C2:D3:E5:F2:0D",
            "A4:6B:6C:9D:E2:FB/C2:9E:1D:E2:3D:A5",
            "A4:6B:6C:9D:E2:FB/D1:8A:4E:71:5D:C1",
            "B4:6B:6C:9D:E2:FB/A4:80:1D:C5:4F:7E",
            "B4:6B:6C:9D:E2:FB/B8:94:A5:FD:F1:0A",
            "B4:6B:6C:9D:E2:FB/C4:72:B3:6F:82:42",
        ]

        expected = [
            os.path.join(bt_linux_sample_01, adapter_device, "info")
            for adapter_device in sample_list
        ]
        actual = get_devices_paths()
        assert sorted(expected) == sorted(actual)

    def test_get_devices(self):
        expected_macs = [
            "A4:BF:C6:D0:E5:FF",
            "B6:C2:D3:E5:F2:0D",
            "C2:9E:1D:E2:3D:A5",
            "D1:8A:4E:71:5D:C1",
            "A4:80:1D:C5:4F:7E",
            "B8:94:A5:FD:F1:0A",
            "C4:72:B3:6F:82:42",
        ]
        actual_macs = [device.mac for device in get_devices()]
        assert sorted(actual_macs) == sorted(expected_macs)

    def test_get_devices__source(self):
        for device in get_devices():
            assert device.is_source_linux()
