import os
import glob
from .bluetooth_device_factory import bluetooth_device_factory

LINUX_BT_DIR = "/var/lib/bluetooth"


def get_adapters_macs():
    """Lists available bluetooths adapeters

    Returns:
        list<str>: kind of ['A4:6B:6C:9D:E2:FB', ...]
    """
    return os.listdir(LINUX_BT_DIR)


def get_adapters_paths():
    """Lists paths to available bluetooths adapters

    Returns:
        list<str>: kind of ['/var/lib/bluetooths/A4:6B:6C:9D:E2:FB', ...]
    """
    return [
        os.path.join(LINUX_BT_DIR, dir_name) for dir_name in os.listdir(LINUX_BT_DIR)
    ]


def get_devices_paths():
    """Lists paths to available bluetooths devices

    Returns:
        list<str>: kind of ['/var/lib/bluetooths/A4:6B:6C:9D:E2:FB/B4:6B:6C:9D:E2:FB/info', ...]
    """
    return glob.glob(os.path.join(LINUX_BT_DIR, "**/info"), recursive=True)


def get_devices():
    """
    Returns:
        list<BluetoothDevice>: linux registred bluetooths devices
    """
    return [
        bluetooth_device_factory(device_path) for device_path in get_devices_paths()
    ]
