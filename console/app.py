import sys
from argparse import ArgumentParser

import bt_linux.devices
from bt_sync_manager import BtSyncManager
from win_mount import locate_windows_mount_points
from windows_registry import WindowsRegistry

from .tools import *


def _argv_parser():
    arg_parser = ArgumentParser(
        prog="bt-dualboot",
        description="Sync bluetooth keys from Linux to Windows.",
    )

    args_list = arg_parser.add_argument_group("List resources")
    args_sync = arg_parser.add_argument_group("Sync keys")

    # fmt: off
    args_list    .add_argument("-l", "--list",          help="[root required] list bluetooth devices",                      action="store_true")
    args_list    .add_argument("--list-win-mounts",     help="list mounted Windows locations",                              action="store_true")
    args_sync    .add_argument("--dry-run",             help="print actions to do without invocation",                      action="store_true")
    args_sync    .add_argument("--win",                 help="[NOT IMPLEMENTED] Windows mount point (advanced usage)",      nargs=1, metavar="MOUNT")
    args_sync    .add_argument("--sync",                help="[NOT IMPLEMENTED] [root required] sync specified device",     nargs="+", metavar="MAC")
    args_sync    .add_argument("--sync-all",            help="[NOT IMPLEMENTED] [root required] sync all paired devices",   action="store_true")
    # fmt: on
    return arg_parser


class Application:
    def __init__(self, opts):
        self.opts = opts
        # fmt: off
        self.__windows_path         = None
        self.__windows_registry     = None
        self.__sync_manager         = None
        # fmt: on

    def _windows_path(self):
        if self.__windows_path == None:
            if self.opts.win != None:
                self.__windows_path = opts.win
            else:
                self.__windows_path = locate_windows_mount_points()[0]

        return self.__windows_path

    def _windows_registry(self):
        require_univocal_windows_location(self.opts.win)
        if self.__windows_registry == None:
            self.__windows_registry = WindowsRegistry(windows_path=self._windows_path())
        return self.__windows_registry

    def _sync_manager(self):
        require_bt_dir_access()

        if self.__sync_manager == None:
            self.__sync_manager = BtSyncManager(self._windows_registry())
        return self.__sync_manager

    def list_win_mounts(self):
        print_header("Windows locations:")

        for mount_point in locate_windows_mount_points():
            print(" " + mount_point)

    def list_devices(self):
        sync_manager = self._sync_manager()
        print_devices_list(
            "Works both in Linux and Windows",
            devices=sync_manager.devices_both_synced(),
        )

        print_devices_list(
            "Needs sync",
            devices=sync_manager.devices_needs_sync(),
            annotation="Following devices available for sync with `--sync-all` or `--sync MAC` options.",
            message_not_found="No device found ready to sync.\nTry pair devices first.",
        )

        print_devices_list(
            "Have to be paired in Windows",
            devices=sync_manager.devices_absent_windows(),
            annotation="Following devices unavailable for sync unless you boot Windows and pair them",
        )

    def sync_all(self):
        sync_manager = self._sync_manager()
        with sync_manager.no_cache():
            devices_for_push = sync_manager.devices_needs_sync()

            print_devices_list(
                "Syncing...",
                devices=devices_for_push,
                message_not_found="Nothing to sync",
            )

            if (
                not self.opts.dry_run
                and devices_for_push != None
                and len(devices_for_push) > 0
            ):
                sync_manager.push(devices_for_push)

        print("...done")

        if self.opts.dry_run:
            print("!! was DRY RUN")

    def run(self):
        if self.opts.list_win_mounts:
            self.list_win_mounts()

        if self.opts.list:
            self.list_devices()

        if self.opts.sync_all:
            self.sync_all()


def parse_argv():
    if len(sys.argv) == 1:
        _argv_parser().print_help()
        print()
        require_chntpw_package()
        return

    opts = _argv_parser().parse_args()

    invariant_and_halt(
        opts.sync_all and opts.sync != None,
        "`--sync-all` can't be used alongside with `--sync MAC`",
    )

    return opts


def main():
    require_linux()
    opts = parse_argv()

    if opts is None:
        return

    if is_debug():
        print(opts)

    require_chntpw_package()
    require_univocal_windows_location(user_selected_windows_location=opts.win)

    app = Application(opts)
    app.run()
