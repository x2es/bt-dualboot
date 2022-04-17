import sys
from argparse import ArgumentParser, ArgumentTypeError
from contextlib import contextmanager
import re

from bt_sync_manager import BtSyncManager, DeviceNotFoundError
from win_mount import locate_windows_mount_points
from windows_registry import WindowsRegistry

from .tools import (
    is_debug,
    require_linux,
    require_chntpw_package,
    require_univocal_windows_location,
    require_bt_dir_access,
    print_header,
    print_devices_list,
)


def mac_str(argument_value):
    value = argument_value.upper()
    if re.match("^[A-F0-9:]+$", value) is None:
        raise ArgumentTypeError(
            "unexpected characters! Allowed letters A-F, digits 0-9 and colon, use space as separator."
        )
    return value


def _argv_parser():
    arg_parser = ArgumentParser(
        prog="bt-dualboot",
        description="Sync bluetooth keys from Linux to Windows.",
    )

    args_list = arg_parser.add_argument_group("List resources")
    args_sync = arg_parser.add_argument_group("Sync keys")

    # fmt: off
    args_list    .add_argument("-l", "--list",          help="[root required] list bluetooth devices",        action="store_true")
    args_list    .add_argument("--list-win-mounts",     help="list mounted Windows locations",                action="store_true")
    args_list    .add_argument("--bot",                 help="parsable output for robots (supported: -l)",    action="store_true")
    args_sync    .add_argument("--dry-run",             help="print actions to do without invocation",        action="store_true")
    args_sync    .add_argument("--win",                 help="Windows mount point (advanced usage)",          nargs=1, metavar="MOUNT")
    args_sync    .add_argument("--sync",                help="[root required] sync specified device",         nargs="+", metavar="MAC", type=mac_str)
    args_sync    .add_argument("--sync-all",            help="[root required] sync all paired devices",       action="store_true")
    # fmt: on
    return arg_parser


@contextmanager
def no_device_error_handler():
    try:
        yield
    except DeviceNotFoundError as err:
        message = err.args[0]
        raise SystemExit(f"ERROR: {message}\nNothing changed.")


class Application:
    def __init__(self, opts):
        self.opts = opts
        # fmt: off
        self.__windows_path         = None
        self.__windows_registry     = None
        self.__sync_manager         = None
        # fmt: on

    def _opts_win_mount_point(self):
        """
        Returns:
            str|None: non-empty --win ARG or None
        """
        mount_point = self.opts.win
        if mount_point is not None:
            mount_point = mount_point[0]

        if mount_point == "":
            mount_point = None

        return mount_point

    def _windows_path(self):
        """
        !cached

        Returns:
            (str): --win ARG or guessed Windows mount point
        """
        if self.__windows_path is None:
            if self._opts_win_mount_point() is not None:
                self.__windows_path = self._opts_win_mount_point()
            else:
                self.__windows_path = locate_windows_mount_points()[0]

        return self.__windows_path

    def _windows_registry(self):
        """
        !cached

        Returns:
            WindowsRegistry
        """
        require_univocal_windows_location(self._opts_win_mount_point())
        if self.__windows_registry is None:
            self.__windows_registry = WindowsRegistry(windows_path=self._windows_path())
        return self.__windows_registry

    def _sync_manager(self):
        """
        !cached

        Returns:
            BtSyncManager
        """
        require_bt_dir_access()

        if self.__sync_manager is None:
            self.__sync_manager = BtSyncManager(self._windows_registry())
        return self.__sync_manager

    def is_dry_run(self):
        return self.opts.dry_run is True

    def list_win_mounts(self):
        print_header("Windows locations:")

        for mount_point in locate_windows_mount_points():
            print(" " + mount_point)

    def list_devices(self):
        sync_manager = self._sync_manager()
        print_devices_list(
            "works",
            "Works both in Linux and Windows",
            devices=sync_manager.devices_both_synced(),
            bot=self.opts.bot,
        )

        print_devices_list(
            "needs_sync",
            "Needs sync",
            devices=sync_manager.devices_needs_sync(),
            annotation="Following devices available for sync with `--sync-all` or `--sync MAC` options.",
            message_not_found="No device found ready to sync.\nTry pair devices first.",
            bot=self.opts.bot,
        )

        print_devices_list(
            "missing_win",
            "Have to be paired in Windows",
            devices=sync_manager.devices_absent_windows(),
            annotation="Following devices unavailable for sync unless you boot Windows and pair them",
            bot=self.opts.bot,
        )

    def sync_devices(self, macs):
        """Sync specified devices

        Args:
          macs (list<str>): list of devices MACs
        """
        with no_device_error_handler():
            self._sync_manager().push(macs, dry_run=self.is_dry_run())
            print(f"synced {', '.join(macs)} successfully")

    def sync_all(self):
        sync_manager = self._sync_manager()
        with sync_manager.no_cache():
            devices_for_push = sync_manager.devices_needs_sync()

            if devices_for_push is None or len(devices_for_push) == 0:
                print("Nothing to sync")
                return

            with no_device_error_handler():
                print_devices_list(
                    "syncing",
                    "Syncing...",
                    devices=devices_for_push,
                    bot=self.opts.bot,
                )

                sync_manager.push(devices_for_push, dry_run=self.is_dry_run())
                print("...done")

    def run(self):
        require_univocal_windows_location(user_selected_location=self._opts_win_mount_point())

        if self.opts.list_win_mounts:
            self.list_win_mounts()

        if self.opts.list:
            self.list_devices()

        if self.opts.sync is not None:
            self.sync_devices(self.opts.sync)

        if self.opts.sync_all:
            self.sync_all()


def parse_argv():
    parser = _argv_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        print()
        require_chntpw_package()
        return

    opts = parser.parse_args()
    blank_states = {
        "list": False,
        "list_win_mounts": False,
        "sync_all": False,
        "sync": None
    }  # fmt: skip

    opts_dict = vars(opts)

    required_specified = [name for name in blank_states.keys() if opts_dict[name] != blank_states[name]]

    if len(required_specified) == 0:
        parser.error("missing required argument")

    if opts.sync_all and opts.sync is not None:
        parser.error("`--sync-all` can't be used alongside with `--sync MAC`")

    return opts


def main():
    require_linux()
    opts = parse_argv()

    if opts is None:
        return

    if is_debug():
        print(opts)

    require_chntpw_package()

    app = Application(opts)
    app.run()
