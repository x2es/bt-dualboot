import os

from .windows_registry import WINDOWS10_REGISTRY_PATH, resolve_path_ci

PROC_MOUNTS = "/proc/mounts"


def mounts_to_try():
    mounts = []
    with open(PROC_MOUNTS) as f:
        for line in f:
            if line.find("/dev") == 0 and line.find("/dev/loop") != 0:
                mount_point = line.split(" ")[1]
                mounts.append(mount_point)

    return mounts


def locate_windows_mount_points():
    win_mount_points = []
    for mount_point in mounts_to_try():
        # Some Linux NTFS mounts are case-sensitive, and not every Windows
        # install has the hive on disk as `SYSTEM`; resolve_path_ci handles
        # both cases.
        resolved = resolve_path_ci(mount_point, WINDOWS10_REGISTRY_PATH)
        if os.path.isfile(resolved):
            win_mount_points.append(mount_point)

    return win_mount_points
