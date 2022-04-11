import pytest
from pytest import fixture

from .shared_fixtures import *
from bt_windows.devices import *

#
# NOTE: helper `wp()` imported from `tests.windows_registry.shared_fixtures`
#

"""
@see tests.bt_windows.shared_fixtures for test set explanation
"""

def test_extract_adapter_mac():
    key = r'ControlSet001\Services\BTHPORT\Parameters\Keys\d46d6d97629b'
    assert extract_adapter_mac(key) == 'D4:6D:6D:97:62:9B'

def test_get_devices(windows_registry, import_devices, test_scheme):
    devices = get_devices(windows_registry)

    for device in devices:
        assert device.mac in list(test_scheme[device.adapter_mac].keys())
        assert device.pairing_key == test_scheme[device.adapter_mac][device.mac]


def test_get_devices__source(windows_registry, import_devices):
    devices = get_devices(windows_registry)
    for device in devices:
        assert device.is_source_windows()
