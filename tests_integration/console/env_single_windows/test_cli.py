from pytest import fixture
import os
import shutil
import filecmp
from operator import itemgetter
from contextlib import contextmanager

from tests.helpers import pytest_unwrap
from tests_integration.helpers import cli_result, snapshot_cli_result, sudo_unlink, debug_shell
from tests.bt_windows.shared_fixtures import (
    test_scheme,
    import_devices,

    # valid for --sync
    MAC_NEED_SYNC_1,
    MAC_NEED_SYNC_2,

    # not valid for --sync
    # MAC_NO_WIN_PAIR_2,
    UNKNOWN_MAC_1,
    UNKNOWN_MAC_2,
)

from bt_dualboot.windows_registry import WindowsRegistry, WINDOWS10_REGISTRY_PATH
from bt_dualboot.console.app import DEFAULT_BACKUP_PATH


OPTS_WIN_MOUNT = ["--win", "/mnt/win"]
WIN_MOUNT_POINT = os.path.join(os.sep, "mnt", "win")
SYSTEM_REG = os.path.join(WIN_MOUNT_POINT, WINDOWS10_REGISTRY_PATH)
CLI_CONTEXT = "[env_single_windows] valid environment with single windows mounted"


def with_win(cmd_opts):
    return [*OPTS_WIN_MOUNT, *cmd_opts]


def filter_devices_macs(stdout, section_id):
    return [
        line.split(" ")[1] for line in stdout.split("\n") if line != "" and line.find(section_id) == 0
    ]


def snapshot_cli(*args, context=CLI_CONTEXT, **kwrd):
    return snapshot_cli_result(*args, context=context, **kwrd)


def snapshot_cli_win(snapshot, cmd_opts, *args, **kwrd):
    actual_opts = [*OPTS_WIN_MOUNT, *cmd_opts]
    return snapshot_cli(snapshot, actual_opts, *args, **kwrd)


@contextmanager
def assert_hive_backup_ok(tmpdir, target_backup_path, should_absent=False):
    """Assert Hive file backup ok

    Creates a copy of Hive file before changes for reference
    Provide FAKETIME= value for the yield
    yield
    Assert backup file match the reference or absent for dry-run
    Cleanup files

    Usage:
        with assert_hive_backup_ok(tmpdir, "/path/to/backup") as fake_time:
            snapshot_cli_result(..., fake_time=fake_time)
            ...

    Args:
        tmpdir (pathlib.Path): temporary dir for test/suite,
            kind of acquired by tmp_path_factory fixture
        target_backup_path (str): target path for Hive backup
        should_absent(bool): when True, asserted backup file doesn't exist
    """

    reg_reference_file_path = tmpdir / "SYSTEM-reference"
    shutil.copy(SYSTEM_REG, reg_reference_file_path)

    yield {"fake_time": "@2020-12-24 20:30:00"}

    backup_file_path = os.path.join(target_backup_path, "SYSTEM-2020-12-24--20-29-59")
    if should_absent is True:
        assert os.path.exists(backup_file_path) is False, "Hive backup should NOT exist"
    else:
        assert filecmp.cmp(
            reg_reference_file_path, backup_file_path, shallow=False
        ), "Hive backup should equal to source"

        os.unlink(reg_reference_file_path)

        # this file were created with super user privileges
        sudo_unlink(backup_file_path)


@fixture(scope="module")
def tmpdir(tmp_path_factory):
    return tmp_path_factory.mktemp("console_app__env_single_windows")


@fixture(scope="module")
def registry_file_path(tmpdir):
    backup_reg = str(tmpdir / "SYSTEM")
    shutil.copy(SYSTEM_REG, backup_reg)
    yield SYSTEM_REG
    shutil.move(backup_reg, SYSTEM_REG)


@fixture(scope="module")
def windows_registry(registry_file_path):
    return WindowsRegistry(registry_file_path)


@fixture(scope="module", autouse=True)
def import_windows_devices_once(windows_registry):
    do_import = pytest_unwrap(import_devices)
    scheme = pytest_unwrap(test_scheme)()

    do_import(windows_registry, scheme)


def manual_test_initial(debug_shell):
    """
    Spawn shell in context with having prepared Linux & Windows bluetooth configs
    invoke using:
        pytest -c manual_pytest.ini
    """
    with debug_shell():
        print("It's initial state with prepared Linux & Windows bluetooth configs")
        print(f"Command-line tip:\n  sudo ./bt-dualboot {' '.join(with_win([]))} ...")


def test_no_args(snapshot):
    """should be identical to -h"""

    for res in snapshot_cli(snapshot, []):
        retcode, stdout = itemgetter("retcode", "stdout")(res)
        assert stdout.find("-h, --help") > 0
        assert retcode == 0


def test_no_args_but_win(snapshot):
    """should be error"""

    for res in snapshot_cli(snapshot, with_win([])):
        assert res["retcode"] == 2


def test_help(snapshot):
    snapshot_cli(snapshot, ["-h"])


# --backup && --no-backup  => Error
def test_no_backup_and_backup(snapshot):
    """should fail with error about incompatibility --backup and --no-backup flags"""
    cmd_opts = ["-l", "--backup", "--no-backup"]
    for res in snapshot_cli_win(snapshot, cmd_opts, sudo=True):
        retcode, stderr = itemgetter("retcode", "stderr")(res)
        assert stderr.find("`--backup` can't be used alongside with `--no-backup`") > 0
        assert retcode == 2


def test_backup_without_sync(snapshot):
    """should fail with error about --backup shouldn't be used without --sync/--sync-all"""
    cmd_opts = ["-l", "--backup"]
    for res in snapshot_cli_win(snapshot, cmd_opts, sudo=True):
        retcode, stderr = itemgetter("retcode", "stderr")(res)
        assert (
            stderr.find("--backup/--no-backup options makes sense only with --sync/--sync-all options")
            > 0
        )
        assert retcode == 2


def test_no_backup_without_sync(snapshot):
    """should fail with error about --no-backup shouldn't be used without --sync/--sync-all"""
    cmd_opts = ["-l", "--no-backup"]
    for res in snapshot_cli_win(snapshot, cmd_opts, sudo=True):
        retcode, stderr = itemgetter("retcode", "stderr")(res)
        assert (
            stderr.find("--backup/--no-backup options makes sense only with --sync/--sync-all options")
            > 0
        )
        assert retcode == 2


# (user) $ -l
def test_list(snapshot):
    """should fail with error about permissions to /var/lib/bluetooth"""
    cmd_opts = ["-l"]
    for res in snapshot_cli_win(snapshot, cmd_opts):
        retcode, stderr = itemgetter("retcode", "stderr")(res)
        assert stderr.find("No Bluetooth devices found") > 0
        assert retcode == 1


# (root) # -l
def test_list_sudo(snapshot):
    """should list bluetooth devices"""
    cmd_opts = ["-l"]
    for res in snapshot_cli_win(snapshot, cmd_opts, sudo=True):
        retcode, stdout = itemgetter("retcode", "stdout")(res)
        assert stdout.find("Works both in Linux and Windows") > 0
        assert stdout.find("Needs sync") > 0
        assert stdout.find("Have to be paired in Windows") > 0
        assert retcode == 0


# (root) # -l --bot
def test_list_bot_sudo(snapshot):
    """should list bluetooth devices"""
    cmd_opts = ["-l", "--bot"]
    for res in snapshot_cli_win(snapshot, cmd_opts, sudo=True):
        assert res["retcode"] == 0


# (root) # -l == --list
def test_list_synonyms():
    headers = ["retcode", "stdout", "stderr"]
    # fmt: off
    res_l       = cli_result(with_win(["-l"]),        sudo=True)
    res_list    = cli_result(with_win(["--list"]),    sudo=True)
    # fmt: on

    assert res_list["retcode"] == 0, "retcode should be 0"

    for key in headers:
        assert res_l[key] == res_list[key], f"{headers[key]} expected to be the same"


class BaseTestSync:
    @fixture(autouse=True)
    def ensure_before_sync(self, tmpdir):
        backup_reg = str(tmpdir / "SYSTEM_before_TestSync")
        shutil.copy(SYSTEM_REG, backup_reg)

        self.assert_needs_sync_and_works(self.initial_needs_sync())

        yield
        shutil.move(backup_reg, SYSTEM_REG)

    @fixture
    def example_tmpdir(self, tmpdir, request):
        """
        Args:
            tmpdir (pathlib.Path): high-order fixture
            request (pytest fixture)
        Returns:
            pathlib.Path: temporary directory for given example
        """
        test_class = self.__class__.__name__
        test_method = request.function.__func__.__name__
        example_dir = tmpdir / test_class / test_method
        example_dir.mkdir(parents=True)
        return example_dir

    @fixture
    def suite_snapshot(self, snapshot):
        """Append class name to snapshot path"""
        default_dir = snapshot.snapshot_dir
        test_name = default_dir.parts[-1]
        test_class = self.__class__.__name__
        snapshot.snapshot_dir = default_dir.parent / test_class / test_name
        return snapshot

    # @override
    def assert_after(self, expected_needs_sync):
        self.assert_needs_sync_and_works(expected_needs_sync)

    def assert_nothing_changed(self):
        self.assert_needs_sync_and_works(self.initial_needs_sync())

    def assert_needs_sync_and_works(self, expected_needs_sync):
        res = cli_result(self.build_opts(["-l", "--bot"]), sudo=True)
        stdout = res["stdout"]
        # fmt: off
        assert set(expected_needs_sync) == set(filter_devices_macs(stdout, "needs_sync"))
        assert set(expected_needs_sync) - set(filter_devices_macs(stdout, "works")) == set(expected_needs_sync),\
            "expected works section doesn't include devices needs sync"
        # fmt: on

    # @override
    def is_dry_run(self):
        return False

    # @override
    def extra_opts(self):
        return []

    def build_opts(self, cmd_opts, unset_backup=False):
        """Append cmd_opts with required opts

        Args:
            cmd_opts (list): list of test's concern options
            unset_backup (bool): prevent appending --backup/--no-backup options
                when backup in concern of the test

        Returns:
            list: full list of cli options for valid invocation
        """
        opts = with_win([*cmd_opts, *self.extra_opts()])
        sync_opts   = set(["--sync", "--sync-all"])  # fmt: skip
        backup_opts = set(["-b", "--backup", "-n", "--no-backup"])

        backup_applicable = len(set(opts) & sync_opts) > 0
        backup_opts_given = len(set(opts) & backup_opts) > 0
        should_unset_backup = backup_opts_given or unset_backup

        if backup_applicable and should_unset_backup is not True:
            opts.append("--no-backup")

        return opts

    def initial_needs_sync(self):
        return [
            MAC_NEED_SYNC_1,
            MAC_NEED_SYNC_2,
        ]


class DryRunMixin:
    def is_dry_run(self):
        return True

    # @override
    def extra_opts(self):
        return ["--dry-run"]

    # @override
    def assert_after(self, expected_needs_sync):
        self.assert_nothing_changed()


class TestBackupSynonyms(BaseTestSync):
    def test_backup_synonyms(self):
        """-b should equal --backup"""
        headers = ["retcode", "stdout", "stderr"]

        # make all devices synced to provide idempotempt invocation next two calls
        cli_result(with_win(["--no-backup", "--sync-all"]), sudo=True)

        # fmt: off
        res_long  = cli_result(with_win(["--backup", "--sync-all"]),  sudo=True)
        res_short = cli_result(with_win(["-b",       "--sync-all"]),  sudo=True)
        # fmt: on

        assert res_long["retcode"] == 0, "retcode should be 0"

        for key in headers:
            assert res_long[key] == res_short[key], f"{key} expected to be the same"

    def test_no_backup_synonyms(self):
        """-n should equal --no-backup"""
        headers = ["retcode", "stdout", "stderr"]

        # make all devices synced to provide idempotempt invocation next two calls
        cli_result(with_win(["--no-backup", "--sync-all"]), sudo=True)

        # fmt: off
        res_long  = cli_result(with_win(["--no-backup", "--sync-all"]),  sudo=True)
        res_short = cli_result(with_win(["-n",          "--sync-all"]),  sudo=True)
        # fmt: on

        assert res_long["retcode"] == 0, "retcode should be 0"

        for key in headers:
            assert res_long[key] == res_short[key], f"{key} expected to be the same"


class TestSync(BaseTestSync):
    def test_require_backup(self, suite_snapshot):
        """should die with backup options suggestion"""
        cmd_opts = self.build_opts(["--sync", MAC_NEED_SYNC_2], unset_backup=True)
        for res in snapshot_cli(suite_snapshot, cmd_opts, sudo=True):
            retcode, stderr = itemgetter("retcode", "stderr")(res)
            expected_error = "Neither backup option given"
            assert stderr.find(expected_error) >= 0
            assert retcode == 2

        self.assert_nothing_changed()

    def test_backup(self, suite_snapshot, example_tmpdir):
        """should backup Hive file to specified path"""
        # subdir doesn't exist, backup method should create it
        target_backup_path = str(example_tmpdir / "subdir")
        cmd_opts = self.build_opts(["--sync", MAC_NEED_SYNC_2, "--backup", target_backup_path])

        with assert_hive_backup_ok(
            example_tmpdir, target_backup_path, should_absent=self.is_dry_run()
        ) as backup_context:
            fake_time = backup_context["fake_time"]
            for res in snapshot_cli(suite_snapshot, cmd_opts, sudo=True, fake_time=fake_time):
                retcode, stdout = itemgetter("retcode", "stdout")(res)
                expected_output = f"synced {MAC_NEED_SYNC_2} successfully"
                assert stdout.find(expected_output) >= 0
                assert retcode == 0

        self.assert_after([MAC_NEED_SYNC_1])

    def test_backup_default(self, suite_snapshot, example_tmpdir):
        """should backup Hive file to default backup path"""
        cmd_opts = self.build_opts(["--sync", MAC_NEED_SYNC_2, "--backup"])

        with assert_hive_backup_ok(
            example_tmpdir, DEFAULT_BACKUP_PATH, should_absent=self.is_dry_run()
        ) as backup_context:
            fake_time = backup_context["fake_time"]
            for res in snapshot_cli(suite_snapshot, cmd_opts, sudo=True, fake_time=fake_time):
                retcode, stdout = itemgetter("retcode", "stdout")(res)
                expected_output = f"synced {MAC_NEED_SYNC_2} successfully"
                assert stdout.find(expected_output) >= 0
                assert retcode == 0

        self.assert_after([MAC_NEED_SYNC_1])

    # --sync MAC    => After: One device to sync left
    def test_single_mac(self, suite_snapshot):
        cmd_opts = self.build_opts(["--sync", MAC_NEED_SYNC_2])
        for res in snapshot_cli(suite_snapshot, cmd_opts, sudo=True):
            retcode, stdout = itemgetter("retcode", "stdout")(res)
            expected_output = f"synced {MAC_NEED_SYNC_2} successfully"
            assert stdout.find(expected_output) >= 0
            assert retcode == 0

        self.assert_after([MAC_NEED_SYNC_1])

    # --sync MAC MAC    => After: No devices to sync
    def test_multipe_macs(self, suite_snapshot):
        cmd_opts = self.build_opts(["--sync", MAC_NEED_SYNC_2, MAC_NEED_SYNC_1])

        for res in snapshot_cli(suite_snapshot, cmd_opts, sudo=True):
            retcode, stdout = itemgetter("retcode", "stdout")(res)
            expected_output = f"synced {MAC_NEED_SYNC_2}, {MAC_NEED_SYNC_1} successfully"
            assert stdout.find(expected_output) >= 0
            assert retcode == 0

        self.assert_after(["NONE"])

    def test__when_no_devices__sync_single(self, suite_snapshot):
        # sync all devices => No devices to sync left
        cli_result(with_win(["--sync-all", "--no-backup"]), sudo=True)

        cmd_opts = self.build_opts(["--sync", MAC_NEED_SYNC_2])
        for res in snapshot_cli(suite_snapshot, cmd_opts, sudo=True):
            retcode, stderr = itemgetter("retcode", "stderr")(res)
            expected_error = f"Can't push {MAC_NEED_SYNC_2}! Not found or already in sync!"
            assert stderr.find(expected_error) >= 0
            assert retcode == 1

    # --sync WRONG_MAC              => Error
    def test_wrong_mac(self, suite_snapshot):
        cmd_opts = self.build_opts(["--sync", UNKNOWN_MAC_1])
        for res in snapshot_cli(suite_snapshot, cmd_opts, sudo=True):
            retcode, stderr = itemgetter("retcode", "stderr")(res)
            expected_error = f"Can't push {UNKNOWN_MAC_1}! Not found"
            assert stderr.find(expected_error) >= 0
            assert retcode == 1

        self.assert_nothing_changed()

    # --sync WRONG_MAC VALID_MAC    => Error
    def test_valid_and_wrong_mac(self, suite_snapshot):
        cmd_opts = self.build_opts(["--sync", MAC_NEED_SYNC_2, UNKNOWN_MAC_2])
        for res in snapshot_cli(suite_snapshot, cmd_opts, sudo=True):
            retcode, stderr = itemgetter("retcode", "stderr")(res)
            expected_error = f"Can't push {UNKNOWN_MAC_2}! Not found"
            assert stderr.find(expected_error) >= 0
            assert retcode == 1

        self.assert_nothing_changed()

    # --sync                        => Error
    def test_missing_mac(self, suite_snapshot):
        cmd_opts = self.build_opts(["--sync"])
        for res in snapshot_cli(suite_snapshot, cmd_opts, sudo=True):
            retcode, stderr = itemgetter("retcode", "stderr")(res)
            expected_error = "error: argument --sync: expected at least one argument"
            assert stderr.find(expected_error) >= 0
            assert retcode == 2

        self.assert_nothing_changed()

    def test_wrong_separator(self, suite_snapshot):
        cmd_opts = self.build_opts(["--sync", f"{MAC_NEED_SYNC_1},{MAC_NEED_SYNC_2}"])
        for res in snapshot_cli(suite_snapshot, cmd_opts, sudo=True):
            retcode, stderr = itemgetter("retcode", "stderr")(res)
            expected_error = "error: argument --sync: unexpected characters! Allowed letters A-F, digits 0-9 and colon, use space as separator."
            assert stderr.find(expected_error) >= 0
            assert retcode == 2

        self.assert_nothing_changed()

    def test_case_insensive(self, suite_snapshot):
        cmd_opts = self.build_opts(["--sync", MAC_NEED_SYNC_2.lower(), MAC_NEED_SYNC_1.lower()])

        for res in snapshot_cli(suite_snapshot, cmd_opts, sudo=True):
            retcode, stdout = itemgetter("retcode", "stdout")(res)
            expected_output = f"synced {MAC_NEED_SYNC_2}, {MAC_NEED_SYNC_1} successfully"
            assert stdout.find(expected_output) >= 0
            assert retcode == 0

        self.assert_after(["NONE"])


class TestSyncDryRun(DryRunMixin, TestSync):
    pass


class TestSyncAll(BaseTestSync):
    def assert_all_synced(self, res):
        retcode, stdout = itemgetter("retcode", "stdout")(res)
        assert stdout.find(MAC_NEED_SYNC_2) >= 0
        assert stdout.find(MAC_NEED_SYNC_1) >= 0
        assert stdout.find("done") >= 0
        assert retcode == 0
        self.assert_after(["NONE"])

    def test_require_backup(self, suite_snapshot):
        """should die with backup options suggestion"""
        cmd_opts = self.build_opts(["--sync-all"], unset_backup=True)
        for res in snapshot_cli(suite_snapshot, cmd_opts, sudo=True):
            retcode, stderr = itemgetter("retcode", "stderr")(res)
            expected_error = "Neither backup option given"
            assert stderr.find(expected_error) >= 0
            assert retcode == 2

        self.assert_nothing_changed()

    def test_backup(self, suite_snapshot, example_tmpdir):
        """should backup Hive file to specified path"""
        # subdir doesn't exist, backup method should create it
        target_backup_path = str(example_tmpdir / "subdir")
        cmd_opts = self.build_opts(["--sync-all", "--backup", target_backup_path])

        with assert_hive_backup_ok(
            example_tmpdir, target_backup_path, should_absent=self.is_dry_run()
        ) as backup_context:
            fake_time = backup_context["fake_time"]
            for res in snapshot_cli(suite_snapshot, cmd_opts, sudo=True, fake_time=fake_time):
                self.assert_all_synced(res)

    def test_backup_default(self, suite_snapshot, tmpdir):
        """should backup Hive file to default backup path"""
        cmd_opts = self.build_opts(["--sync-all", "--backup"])

        with assert_hive_backup_ok(
            tmpdir, DEFAULT_BACKUP_PATH, should_absent=self.is_dry_run()
        ) as backup_context:
            fake_time = backup_context["fake_time"]
            for res in snapshot_cli(suite_snapshot, cmd_opts, sudo=True, fake_time=fake_time):
                self.assert_all_synced(res)

    # --sync-all    => After: No devices to sync
    def test_sync_all(self, suite_snapshot):
        cmd_opts = self.build_opts(["--sync-all"])
        for res in snapshot_cli(suite_snapshot, cmd_opts, sudo=True):
            retcode, stdout = itemgetter("retcode", "stdout")(res)
            assert stdout.find(MAC_NEED_SYNC_2) >= 0
            assert stdout.find(MAC_NEED_SYNC_1) >= 0
            assert stdout.find("done") >= 0
            assert retcode == 0

        self.assert_after(["NONE"])

    # --sync-all --bot    => After: No devices to sync
    def test_sync_all_bot(self, suite_snapshot):
        cmd_opts = self.build_opts(["--sync-all", "--bot"])
        for res in snapshot_cli(suite_snapshot, cmd_opts, sudo=True):
            retcode, stdout = itemgetter("retcode", "stdout")(res)
            assert stdout.find(MAC_NEED_SYNC_2) >= 0
            assert stdout.find(MAC_NEED_SYNC_1) >= 0
            assert stdout.find("done") >= 0
            assert retcode == 0

        self.assert_after(["NONE"])

    # --sync-all    => After: No devices to sync
    def test__when_no_devices__sync_all(self, suite_snapshot):
        cmd_opts = self.build_opts(["--sync-all"])

        # sync all devices => No devices to sync left
        cli_result(cmd_opts, sudo=True)

        for res in snapshot_cli(suite_snapshot, cmd_opts, sudo=True):
            assert res["retcode"] == 0

        self.assert_after(["NONE"])

    # --sync-all --sync MAC     => Error
    def test_sync_all_and_sync(self, suite_snapshot):
        cmd_opts = self.build_opts(["--sync-all", "--sync", "123"])
        for res in snapshot_cli(suite_snapshot, cmd_opts, sudo=True):
            assert res["retcode"] == 2

        self.assert_nothing_changed()


class TestSyncAllDryRun(DryRunMixin, TestSyncAll):
    pass
