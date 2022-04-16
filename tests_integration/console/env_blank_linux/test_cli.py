from tests_integration.helpers import snapshot_cli_result
from operator import itemgetter


def snapshot_cli(*args, **kwrd):
    context = "[env_blank_linux] chntpw not installed, windows not mounted"
    return snapshot_cli_result(*args, context=context, **kwrd)


def test_no_args(snapshot):
    """should be identical to -h"""
    for res in snapshot_cli(snapshot, []):
        retcode, stdout = itemgetter("retcode", "stdout")(res)
        assert retcode == 1
        assert stdout.find("-h, --help") > 0


def test_help(snapshot):
    snapshot_cli(snapshot, ["-h"])


def test_list(snapshot):
    """should fails with error about missing `reged`"""
    for res in snapshot_cli(snapshot, ["-l"]):
        retcode, stderr = itemgetter("retcode", "stderr")(res)
        assert retcode != 0
        assert stderr.find("reged") > 0
