from bt_dualboot import APP_NAME, __version__
from tests_integration.helpers import snapshot_cli_result, debug_shell
from operator import itemgetter


def snapshot_cli(*args, **kwrd):
    context = "[env_blank_linux] chntpw not installed, windows not mounted"
    return snapshot_cli_result(*args, context=context, **kwrd)


def manual_test_initial(debug_shell):
    """
    Spawn shell in context with having prepared Linux & Windows bluetooth configs
    invoke using:
        pytest -c manual_pytest.ini
    """
    with debug_shell():
        print("It's initial state with prepared Linux & Windows bluetooth configs")
        print("Command-line tip:\n  sudo ./bt-dualboot ...")


def test_no_args(snapshot):
    """should be identical to -h"""
    for res in snapshot_cli(snapshot, []):
        retcode, stdout = itemgetter("retcode", "stdout")(res)
        assert retcode == 1
        assert stdout.find("-h, --help") > 0


def test_help(snapshot):
    snapshot_cli(snapshot, ["-h"])


def test_version(snapshot):
    for res in snapshot_cli(snapshot, ["--version"]):
        retcode, stdout = itemgetter("retcode", "stdout")(res)
        assert retcode == 0
        assert stdout == f"{APP_NAME} {__version__}\n"


def test_list(snapshot):
    """should fails with error about missing `reged`"""
    for res in snapshot_cli(snapshot, ["-l"]):
        retcode, stderr = itemgetter("retcode", "stderr")(res)
        assert retcode != 0
        assert stderr.find("reged") > 0
