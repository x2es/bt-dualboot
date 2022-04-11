from tests_integration.helpers import snapshot_cli_result

def test_no_args(snapshot):
    """should be identical to -h"""
    for retcode, stdout, stderr in snapshot_cli_result(snapshot, []):
        assert retcode == 1
        assert stdout.find('-h, --help') > 0


def test_help(snapshot):
    snapshot_cli_result(snapshot, ['-h'])


def test_list(snapshot):
    """should fails with error about missing `reged`"""
    for retcode, stdout, stderr in snapshot_cli_result(snapshot, ['-l']):
        assert retcode != 0
        assert stderr.find('reged') > 0


