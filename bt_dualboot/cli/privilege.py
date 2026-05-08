"""Runtime privilege elevation.

The tool reads `/var/lib/bluetooth/` and writes the Windows SYSTEM hive via
`reged`, both of which require root. To allow user-level installs (e.g.
`uv tool install bt-dualboot`, `pipx install bt-dualboot`) we re-exec the
current command under `sudo` when a root-needing action is requested while
running as a non-root user. `sudo` then prompts for the password on the TTY.
"""

import os
import shlex
import shutil
import sys


def is_debug():
    return os.environ.get("DEBUG") == "1"


def action_requires_root(opts):
    """Return True if the requested action needs to read/write root-only files.

    `--list-win-mounts`, `--version`, and the help screen do not need root.
    """
    return bool(
        getattr(opts, "list", False)
        or getattr(opts, "sync_all", False)
        or getattr(opts, "sync", None) is not None
    )


def _build_reexec_argv():
    """Pick the safest argv to hand to sudo for re-executing this command.

    Prefer the original entry script (e.g. `~/.local/bin/bt-dualboot`) if it
    exists and is executable; its shebang points at the right interpreter.
    Otherwise fall back to `python -m bt_dualboot`, which works for
    `python -m bt_dualboot` invocations where argv[0] is `__main__.py`.
    """
    argv0 = sys.argv[0]
    if argv0 and os.path.isfile(argv0) and os.access(argv0, os.X_OK):
        return [argv0, *sys.argv[1:]]
    return [sys.executable, "-m", "bt_dualboot", *sys.argv[1:]]


def elevate_via_sudo():
    """Re-execute the current command under `sudo`. Does not return on success.

    Raises SystemExit with a clear message if sudo is unavailable.
    """
    if os.geteuid() == 0:
        return

    sudo_path = shutil.which("sudo")
    if sudo_path is None:
        raise SystemExit(
            "ERROR: This action requires root privileges, but `sudo` was not found "
            "on PATH. Either install sudo, run this command as root, or pass "
            "`--no-elevate` and re-invoke under root yourself."
        )

    inner = _build_reexec_argv()
    # `--preserve-env=DEBUG` keeps the debug toggle across the sudo boundary.
    cmd = [sudo_path, "--preserve-env=DEBUG", "--", *inner]

    if is_debug():
        print(
            "DEBUG: re-executing under sudo: "
            + " ".join(shlex.quote(a) for a in cmd),
            file=sys.stderr,
        )

    print(
        "[bt-dualboot] root privileges required; re-executing under sudo "
        "(use --no-elevate to disable)",
        file=sys.stderr,
    )
    os.execvp(sudo_path, cmd)
