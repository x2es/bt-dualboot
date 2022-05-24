from bt_dualboot.bt_linux.bluetooth_device_factory import *
import os

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_samples")
SMPL_BT_SAMPLE_01 = os.path.join(SAMPLES_DIR, "bt_sample_01")
SAMPLE_DEVICE_INFO_PATH = os.path.join(
    SMPL_BT_SAMPLE_01, "A4:6B:6C:9D:E2:FB", "B6:C2:D3:E5:F2:0D", "info"
)
SAMPLE_DEVICE_INFO_PATH_NO_LINKKEY = os.path.join(
    SMPL_BT_SAMPLE_01, "A4:6B:6C:9D:E2:FB", "22:94:90:56:EE:38", "info"
)


def test_extract_macs():
    expected = {"device_mac": "B6:C2:D3:E5:F2:0D", "adapter_mac": "A4:6B:6C:9D:E2:FB"}
    assert extract_macs(SAMPLE_DEVICE_INFO_PATH) == expected


def test_extract_info():
    expected = {
        "name": "DEV-1-02-Name",
        "class": "0x000540",
        "pairing_key": "A515CBE4E8F2E236FF999C0A53369EF6",
    }
    assert extract_info(SAMPLE_DEVICE_INFO_PATH) == expected


def test_extract_info_no_linkkey():
    expected = {
        "name": "DEV-1-02-Name",
        "class": "0x000540",
        "pairing_key": None,
    }
    assert extract_info(SAMPLE_DEVICE_INFO_PATH_NO_LINKKEY) == expected


def test_bluetooth_device_factory():
    device = bluetooth_device_factory(SAMPLE_DEVICE_INFO_PATH)

    # fmt: off
    assert device.__class__.__name__    == "BluetoothDevice"
    assert device.klass                 == "0x000540"
    assert device.mac                   == "B6:C2:D3:E5:F2:0D"
    assert device.name                  == "DEV-1-02-Name"
    assert device.pairing_key           == "A515CBE4E8F2E236FF999C0A53369EF6"
    # fmt: on

def test_bluetooth_device_factory_no_linkkey():
    device = bluetooth_device_factory(SAMPLE_DEVICE_INFO_PATH_NO_LINKKEY)

    # fmt: off
    assert device.__class__.__name__    == "BluetoothDevice"
    assert device.klass                 == "0x000540"
    assert device.mac                   == "22:94:90:56:EE:38"
    assert device.name                  == "DEV-1-02-Name"
    assert device.pairing_key           == None
    # fmt: on
