import os
import subprocess
import sys
from pathlib import Path
from contextlib import contextmanager
from operator import itemgetter

from pytest import fixture


@fixture(scope="session")
def debug_shell(request):
    """Spawn debug /bin/bash in middle of pytest session.
    Useful to debug Docker context between setup and teardown states.
    """

    @contextmanager
    def runner(shell="/bin/bash", cmd_opts=[], *subprocess_args, **subprocess_kwrd):
        """Invokes shell using subprocess.run

        Usage:
            def test_foo(debug_shell):
                ...
                with debug_shell():   # /bin/bash by default
                  pass
                ...
                with debug_shell('/bin/sh', ['-c', 'echo foo'], capture_output=False):
                  pass
                ...
                with debug_shell():
                  print(some_context)       # yields between disabling capturing
                                            # and spaning shell

        Args:
            shell (str): [default: /bin/bash] path to shell
            cmd_opts (list): list of command line options in subprocess.run format
            subprocess_args (list)
            subprocess_kwrd (dict)
        """
        capman = request.config.pluginmanager.getplugin("capturemanager")
        capman.suspend_global_capture(in_=True)
        print("\n\nDEBUG: CAPTURE DISABLED")
        yield
        print("\nPYTEST SYSTEM SHELL STARTED")
        subprocess.run([shell, *cmd_opts], *subprocess_args, **subprocess_kwrd)
        print("\n\nPYTEST SYSTEM SHELL EXIT")
        capman.resume_global_capture()

    return runner


def cli_name():
    return "bt-dualboot"


def project_root():
    """
    Returns:
        str: project's root irrelative to current directory
    """
    return Path(__file__).parent.parent


def cli_result(cmd_opts, sudo=False):
    """
    Invokes cli with given comand line options
    Captures and yield's return code, stdout and stderr

    Args:
        cmd_opts (list): list of command options for subprocess.run
        sudo (bool): invoke with sudo

    Returns:
        dict:
            retcode (int): exit code of the command
            stdout (str)
            stderr (str)
            cmd (str): invoked command

    """
    exec_path = os.path.join(project_root(), cli_name())
    cmd = [exec_path, *cmd_opts]
    if sudo is True:
        cmd.insert(0, "sudo")

    res = subprocess.run(
        cmd,
        capture_output=True,
    )

    stdout = res.stdout.decode(sys.stdout.encoding)
    stderr = res.stderr.decode(sys.stderr.encoding)
    # fmt: off
    return {
        "retcode": res.returncode,
        "stdout":  stdout,
        "stderr":  stderr,
        "cmd":     cmd
    }
    # fmt: on


def snapshot_cli_result(snapshot_tool, cmd_opts, sudo=False, context=None):
    """
    Invokes cli with given comand line options
    Captures and yield's return code, stdout and stderr
    Saves snapshot for stdout and returncode+stderr

    Args:
        snapshot_tool (pytest_snapshot.plugin.Snapshot): `snapshot` fixture from pytest-snapshot
        cmd_opts (list): list of command options for subprocess.run
        sudo (bool): invoke with sudo

    Yields:
        dict: @see cli_result
            retcode (int): exit code of the command
            stdout (str)
            stderr (str)
            cmd (str): invoked command
    """
    res = cli_result(cmd_opts, sudo)
    retcode, stdout, stderr, cmd = itemgetter("retcode", "stdout", "stderr", "cmd")(res)

    output = [
        f"CMD: {' '.join(cmd)}",
        f"RETCODE={retcode}",
        "STDOUT:\n=======",
        stdout,
        "-------------------------------------------------------------",
        "STDERR:\n=======",
        stderr,
        "-------------------------------------------------------------",
    ]

    if context is not None:
        output.insert(0, f"CONTEXT: {context}")

    output = "\n".join(output)

    try:
        yield res
        snapshot_tool.assert_match(output, "output")
    except Exception as err:
        message = err.args[0] or ""
        print("SNAPSHOT CONTENT:")
        print(output)
        print(f"\n{err.__class__.__name__}: {message}\n{err.args[1:]}")
        raise err
