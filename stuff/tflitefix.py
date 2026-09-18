import glob
import os
import shutil
from stuff.general import General
from tools.logger import Logger


class TfliteFix(General):
    id = "tflitefix"
    partition = "system"
    TARGET_OFFSET = 0x2E9204
    PATCH_BYTES = b"\xc0\x03\x5f\xd6"  # ret in AArch64 little-endian

    def __init__(self, android_version="13") -> None:
        super().__init__()

    def download(self):
        pass

    @property
    def skip_extract(self):
        return True

    def copy(self):
        pass

    def extra1(self):
        """Applies binary patch to libtensorflowlite.so in installed apps"""
        search_paths = [
            os.path.expanduser("~/.local/share/waydroid/data/app/~~*==/*/lib/arm64/libtensorflowlite.so"),
            "/var/lib/waydroid/data/app/~~*==/*/lib/arm64/libtensorflowlite.so",
        ]
        found = []
        for p in search_paths:
            found.extend(glob.glob(p))

        if not found:
            Logger.warning("No installed apps with libtensorflowlite.so found in Waydroid data.")
            return

        for lib_path in found:
            try:
                with open(lib_path, "rb") as f:
                    data = bytearray(f.read())

                if len(data) > self.TARGET_OFFSET + 4:
                    if bytes(data[self.TARGET_OFFSET:self.TARGET_OFFSET+4]) == self.PATCH_BYTES:
                        Logger.info(f"Patch already applied to {lib_path}")
                        continue

                    backup = lib_path + ".orig"
                    if not os.path.exists(backup):
                        shutil.copy2(lib_path, backup)

                    data[self.TARGET_OFFSET:self.TARGET_OFFSET+4] = self.PATCH_BYTES
                    with open(lib_path, "wb") as f:
                        f.write(data)
                    os.chmod(lib_path, 0o755)
                    Logger.info(f"Successfully patched {lib_path}")
            except Exception as e:
                Logger.error(f"Failed to patch {lib_path}: {e}")

    def extra2(self):
        """Restores original libtensorflowlite.so from backup"""
        search_paths = [
            os.path.expanduser("~/.local/share/waydroid/data/app/~~*==/*/lib/arm64/libtensorflowlite.so.orig"),
            "/var/lib/waydroid/data/app/~~*==/*/lib/arm64/libtensorflowlite.so.orig",
        ]
        for p in search_paths:
            for orig in glob.glob(p):
                target = orig[:-5]
                try:
                    shutil.copy2(orig, target)
                    os.remove(orig)
                    os.chmod(target, 0o755)
                    Logger.info(f"Restored {target}")
                except Exception as e:
                    Logger.error(f"Failed to restore {target}: {e}")
