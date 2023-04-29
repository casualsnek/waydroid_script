import os
import shutil
from stuffs.general import General
from tools.helper import run
from tools.logger import Logger
from tools.container import use_overlayfs

class Ndk(General):
    id = "libndk"
    partition = "system"
    dl_link = "https://github.com/supremegamers/vendor_google_proprietary_ndk_translation-prebuilt/archive/181d9290a69309511185c4417ba3d890b3caaaa8.zip"
    dl_file_name = "libndktranslation.zip"
    extract_to = "/tmp/libndkunpack"
    act_md5 = "0beff55f312492f24d539569d84f5bfb"
    apply_props = {
        "ro.product.cpu.abilist": "x86_64,x86,armeabi-v7a,armeabi,arm64-v8a",
        "ro.product.cpu.abilist32": "x86,armeabi-v7a,armeabi",
        "ro.product.cpu.abilist64": "x86_64,arm64-v8a",
        "ro.dalvik.vm.native.bridge": "libndk_translation.so",
        "ro.enable.native.bridge.exec": None,
        "ro.vendor.enable.native.bridge.exec": None,
        "ro.vendor.enable.native.bridge.exec64": None,
        "ro.ndk_translation.version": "0.2.3",
        "ro.dalvik.vm.isa.arm": "x86",
        "ro.dalvik.vm.isa.arm64": "x86_64"
    }
    files = [
            "bin/arm",
            "bin/arm64",
            "bin/ndk_translation_program_runner_binfmt_misc",
            "bin/ndk_translation_program_runner_binfmt_misc_arm64",
            "etc/binfmt_misc",
            "etc/ld.config.arm.txt",
            "etc/ld.config.arm64.txt",
            "etc/init/ndk_translation.rc",
            "lib/arm",
            "lib64/arm64",
            "lib/libndk*",
            "lib64/libndk*"
        ]
    def __init__(self, android_version="11") -> None:
        super().__init__()
        if android_version=="11":
            self.apply_props["ro.enable.native.bridge.exec"] = "1"
        elif android_version=="13":
            self.apply_props["ro.vendor.enable.native.bridge.exec"] = "1"
            self.apply_props["ro.vendor.enable.native.bridge.exec64"] = "1"


    def copy(self):
        run(["chmod", "+x", self.extract_to, "-R"])
        Logger.info("Copying libndk library files ...")
        shutil.copytree(os.path.join(self.extract_to, "vendor_google_proprietary_ndk_translation-prebuilt-181d9290a69309511185c4417ba3d890b3caaaa8", "prebuilts"), os.path.join(self.copy_dir, self.partition), dirs_exist_ok=True)
        init_path = os.path.join(self.copy_dir, self.partition, "etc", "init", "ndk_translation.rc")
        os.chmod(init_path, 0o644)
        