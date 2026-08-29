#!/usr/bin/env python3
"""Regression test for Magisk.setup() permissions on the /data/adb/magisk copy.

install() runs copy() -> extra1() -> set_perm(). set_perm() only walks self.files,
which are paths under copy_dir (the overlay), so the copy that setup() makes into
<data>/adb/magisk keeps the 0644 the binaries inherit from the apk extraction.

A non-executable /data/adb/magisk/magisk64 makes magisk_env() abort at post-fs-data.
Root still works (it runs from the overlay copy), but Zygisk never initialises and
the Magisk app reports "Zygisk: No" with no error explaining why.

Runs as an ordinary user, needs no Waydroid install and no extra dependencies:

    python3 tests/test_magisk_setup_perms.py
"""

import os
import shutil
import stat
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import stuff.magisk as magisk_module
from stuff.magisk import Magisk

MAGISK_BINARIES = [
    "magisk64",
    "magiskinit",
    "magiskboot",
    "magiskpolicy",
    "busybox",
    "util_functions.sh",
]


def make_overlay(base):
    """Mimic the tree copy() leaves behind: binaries written 0644 by shutil.copyfile."""
    magisk_dir = os.path.join(base, "system", "etc", "init", "magisk")
    os.makedirs(os.path.join(magisk_dir, "chromeos"), exist_ok=True)
    for name in MAGISK_BINARIES:
        path = os.path.join(magisk_dir, name)
        with open(path, "wb") as f:
            f.write(b"\x7fELF placeholder")
        os.chmod(path, 0o644)
    nested = os.path.join(magisk_dir, "chromeos", "futility")
    with open(nested, "wb") as f:
        f.write(b"placeholder")
    os.chmod(nested, 0o644)
    return magisk_dir


def file_modes(root):
    modes = {}
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            path = os.path.join(dirpath, name)
            modes[os.path.relpath(path, root)] = stat.S_IMODE(os.stat(path).st_mode)
    return modes


def test_plain_copytree_loses_exec_bit():
    """Document the original behaviour: a bare copytree leaves the binaries 0644."""
    base = tempfile.mkdtemp()
    try:
        src = make_overlay(base)
        dst = os.path.join(base, "data", "adb", "magisk")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copytree(src, dst, dirs_exist_ok=True)

        modes = file_modes(dst)
        assert modes["magisk64"] == 0o644, (
            "expected the pre-fix behaviour to reproduce, got %o" % modes["magisk64"]
        )
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_setup_makes_data_copy_executable():
    """setup() must leave every file and dir in <data>/adb/magisk executable."""
    base = tempfile.mkdtemp()
    try:
        make_overlay(base)
        data_dir = os.path.join(base, "data")
        os.makedirs(data_dir, exist_ok=True)

        original_get_data_dir = magisk_module.get_data_dir
        original_info = magisk_module.Logger.info
        magisk_module.get_data_dir = lambda: data_dir
        magisk_module.Logger.info = lambda *a, **k: None

        class StubMagisk(Magisk):
            @property
            def copy_dir(self):
                return base

        try:
            StubMagisk().setup()
        finally:
            magisk_module.get_data_dir = original_get_data_dir
            magisk_module.Logger.info = original_info

        dst = os.path.join(data_dir, "adb", "magisk")
        modes = file_modes(dst)
        assert modes, "setup() copied nothing"

        not_executable = {n: oct(m) for n, m in modes.items() if m != 0o755}
        assert not not_executable, "files left non-0755: %s" % not_executable

        assert stat.S_IMODE(os.stat(dst).st_mode) == 0o755
        nested = os.path.join(dst, "chromeos")
        assert stat.S_IMODE(os.stat(nested).st_mode) == 0o755, "nested dir not fixed"
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_setup_is_idempotent():
    base = tempfile.mkdtemp()
    try:
        make_overlay(base)
        data_dir = os.path.join(base, "data")
        os.makedirs(data_dir, exist_ok=True)

        original_get_data_dir = magisk_module.get_data_dir
        original_info = magisk_module.Logger.info
        magisk_module.get_data_dir = lambda: data_dir
        magisk_module.Logger.info = lambda *a, **k: None

        class StubMagisk(Magisk):
            @property
            def copy_dir(self):
                return base

        try:
            StubMagisk().setup()
            StubMagisk().setup()
        finally:
            magisk_module.get_data_dir = original_get_data_dir
            magisk_module.Logger.info = original_info

        dst = os.path.join(data_dir, "adb", "magisk")
        assert all(m == 0o755 for m in file_modes(dst).values())
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_perm_helper_tolerates_missing_dir():
    Magisk().set_data_magisk_perm(os.path.join(tempfile.gettempdir(), "definitely-not-here"))


def main():
    tests = [
        test_plain_copytree_loses_exec_bit,
        test_setup_makes_data_copy_executable,
        test_setup_is_idempotent,
        test_perm_helper_tolerates_missing_dir,
    ]
    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as exc:
            failed += 1
            print("FAIL %s: %s" % (test.__name__, exc))
        except Exception as exc:  # noqa: BLE001 - surface anything unexpected
            failed += 1
            print("ERROR %s: %r" % (test.__name__, exc))
        else:
            print("ok   %s" % test.__name__)
    if failed:
        print("\n%d test(s) failed" % failed)
        return 1
    print("\nall %d tests passed" % len(tests))
    return 0


if __name__ == "__main__":
    sys.exit(main())
