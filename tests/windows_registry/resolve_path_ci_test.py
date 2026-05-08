import os

from bt_dualboot.windows_registry import resolve_path_ci, WindowsRegistry


def _touch(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w"):
        pass


class TestResolvePathCi:
    def test_exact_match(self, tmp_path):
        target = tmp_path / "Windows" / "System32" / "config" / "SYSTEM"
        _touch(str(target))

        resolved = resolve_path_ci(str(tmp_path), os.path.join("Windows", "System32", "config", "SYSTEM"))
        assert resolved == str(target)

    def test_case_mismatch_in_filename(self, tmp_path):
        # On disk: lowercase `system`, upper-case parent dirs.
        target = tmp_path / "Windows" / "System32" / "config" / "system"
        _touch(str(target))

        resolved = resolve_path_ci(str(tmp_path), os.path.join("Windows", "System32", "config", "SYSTEM"))
        assert resolved == str(target), "should walk past the upper-case 'SYSTEM' request and find lower-case 'system'"

    def test_case_mismatch_in_directory(self, tmp_path):
        # On disk: every component in lower-case.
        target = tmp_path / "windows" / "system32" / "config" / "system"
        _touch(str(target))

        resolved = resolve_path_ci(str(tmp_path), os.path.join("Windows", "System32", "config", "SYSTEM"))
        assert resolved == str(target)

    def test_missing_segment_returns_original_join(self, tmp_path):
        # No matching file at all: helper should return base+relative unchanged
        # so the caller's downstream error message still references what was asked for.
        relative = os.path.join("Windows", "System32", "config", "SYSTEM")
        resolved = resolve_path_ci(str(tmp_path), relative)
        assert resolved == os.path.join(str(tmp_path), relative)

    def test_nonexistent_base_returns_original_join(self, tmp_path):
        bogus = str(tmp_path / "does-not-exist")
        relative = os.path.join("Windows", "System32", "config", "SYSTEM")
        resolved = resolve_path_ci(bogus, relative)
        assert resolved == os.path.join(bogus, relative)


class TestWindowsRegistryRegistryFile:
    """WindowsRegistry should pick up a lower-case `system` hive on a case-sensitive FS."""

    def test_lowercase_system_resolved(self, tmp_path):
        target = tmp_path / "Windows" / "System32" / "config" / "system"
        _touch(str(target))

        registry = WindowsRegistry(windows_path=str(tmp_path))
        assert registry._registry_file() == str(target)
