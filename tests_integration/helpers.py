import os
import subprocess
import sys
from pathlib import Path

def cli_name():
    return 'bt-dualboot'


def project_root():
    """
    Returns:
        str: project's root irrelative to current directory
    """
    return Path(__file__).parent.parent


def snapshot_cli_result(snapshot_tool, cmd_ops):
    """
    Invokes cli with given comand line options
    Captures and yield's return code, stdout and stderr
    Saves snapshot for stdout and returncode+stderr

    Yields:
        retcode (int): exit code of the command
        stdout (str)
        stderr (str)

    Args:
        snapshot_tool (pytest_snapshot.plugin.Snapshot): `snapshot` fixture from pytest-snapshot
        cmd_ops (list): list of command options for subprocess.run
    """
    exec_path = os.path.join(project_root(), cli_name())
    res = subprocess.run( [exec_path, *cmd_ops], capture_output=True,)

    stdout = res.stdout.decode(sys.stdout.encoding)
    stderr = res.stderr.decode(sys.stderr.encoding)

    yield res.returncode, stdout, stderr

    retcode_and_stderr = f'{res.returncode}\n{stderr}'

    snapshot_tool.assert_match(stdout,               'stdout')
    snapshot_tool.assert_match(retcode_and_stderr,   'retcode_and_stderr')


