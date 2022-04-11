from pytest import fixture
from unittest.mock import patch
from bt_sync_manager import BtSyncManager
from bluetooth_device import BluetoothDevice

# EXPERIMENTAL:
# import windows_registry_test fixtures
# implies usage of `tests.bt_windows.shared_fixtures` fixtures
#   which implies `tests.windows_registry.shared_fixtures`
#   with it's `windows_registry_test/sample_data/`
from tests.bt_windows.shared_fixtures import *
from tests.bt_linux.shared_fixtures import *


SAMPLE_PUSH_MAC1 = "C2:9E:1D:E2:3D:A5"
SAMPLE_PUSH_MAC2 = "B8:94:A5:FD:F1:0A"


@fixture
def sync_manager(import_devices, windows_registry):
    return BtSyncManager(windows_registry)

@fixture
@patch("bt_linux.devices.LINUX_BT_DIR", bt_linux_sample_01_unwrapped())
def just_pushed(sync_manager):
    sync_manager.push([SAMPLE_PUSH_MAC1])
    sync_manager.flush_cache()


@patch("bt_linux.devices.LINUX_BT_DIR", bt_linux_sample_01_unwrapped())
class TestBtSyncManager__Initial:
    def test_devices_both_synced(self, sync_manager):
        expected_macs = ["A4:BF:C6:D0:E5:FF", "B6:C2:D3:E5:F2:0D", "A4:80:1D:C5:4F:7E"]

        devices = sync_manager.devices_both_synced()
        devices_macs = [device.mac for device in devices]
        assert sorted(devices_macs) == sorted(expected_macs)

    def test_devices_needs_sync(self, sync_manager):
        expected_macs = [
            "C2:9E:1D:E2:3D:A5",
            "B8:94:A5:FD:F1:0A",
        ]

        devices = sync_manager.devices_needs_sync()
        devices_macs = [device.mac for device in devices]
        assert sorted(devices_macs) == sorted(expected_macs)

    def test_devices_absent_windows(self, sync_manager):
        expected_macs = ["D1:8A:4E:71:5D:C1", "C4:72:B3:6F:82:42"]

        devices = sync_manager.devices_absent_windows()
        devices_macs = [device.mac for device in devices]
        assert sorted(devices_macs) == sorted(expected_macs)


@patch("bt_linux.devices.LINUX_BT_DIR", bt_linux_sample_01_unwrapped())
class TestBtSyncManager__AfterSync:
    def test_devices_both_synced(self, sync_manager, just_pushed):
        expected_macs = [
            "A4:BF:C6:D0:E5:FF",
            "B6:C2:D3:E5:F2:0D",
            "A4:80:1D:C5:4F:7E",
            "C2:9E:1D:E2:3D:A5",
        ]

        devices = sync_manager.devices_both_synced()
        devices_macs = [device.mac for device in devices]
        assert sorted(devices_macs) == sorted(expected_macs)


    def test_devices_needs_sync(self, sync_manager, just_pushed):
        expected_macs = [
            "B8:94:A5:FD:F1:0A",
        ]

        devices = sync_manager.devices_needs_sync()
        devices_macs = [device.mac for device in devices]
        assert sorted(devices_macs) == sorted(expected_macs)


    def test_devices_absent_windows(self, sync_manager, just_pushed):
        expected_macs = ["D1:8A:4E:71:5D:C1", "C4:72:B3:6F:82:42"]

        devices = sync_manager.devices_absent_windows()
        devices_macs = [device.mac for device in devices]
        assert sorted(devices_macs) == sorted(expected_macs)


@patch("bt_linux.devices.LINUX_BT_DIR", bt_linux_sample_01_unwrapped())
class TestBtSyncManager__push:
    def assert_effect(self, sync_manager):
        expected_macs = [ "B8:94:A5:FD:F1:0A" ]

        devices = sync_manager.devices_needs_sync()
        devices_macs = [device.mac for device in devices]
        assert sorted(devices_macs) == sorted(expected_macs)


    def test_ensure_push_resets_cache(self, sync_manager):
        # populate & corrupt cache
        sync_manager.devices_needs_sync()
        sync_manager.index_cache[SAMPLE_PUSH_MAC1].pop()

        sync_manager.push(BluetoothDevice(mac=SAMPLE_PUSH_MAC1))
        # EXPECT no exceptions raised
        assert True


    def test_push_accept_single_mac(self, sync_manager):
        sync_manager.push(SAMPLE_PUSH_MAC1)
        self.assert_effect(sync_manager)


    def test_push_accept_list_of_macs(self, sync_manager):
        sync_manager.push([SAMPLE_PUSH_MAC1])
        self.assert_effect(sync_manager)


    def test_push_accept_single_bt_instance(self, sync_manager):
        sync_manager.push(BluetoothDevice(mac=SAMPLE_PUSH_MAC1))
        self.assert_effect(sync_manager)


    def test_push_accept_list_of_bt_instances(self, sync_manager):
        sync_manager.push([BluetoothDevice(mac=SAMPLE_PUSH_MAC1)])
        self.assert_effect(sync_manager)

    def test_push_updates_multiple_devices(self, sync_manager):
        sync_manager.push([SAMPLE_PUSH_MAC1, SAMPLE_PUSH_MAC2])
        assert sync_manager.devices_needs_sync() == []
