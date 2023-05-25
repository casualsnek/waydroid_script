import os
import re
import shutil
from stuff.general import General
from tools.logger import Logger

class Ndk(General):
    id = "libndk"
    partition = "system"
    dl_links = {
        "11": ["https://github.com/supremegamers/vendor_google_proprietary_ndk_translation-prebuilt/archive/9324a8914b649b885dad6f2bfd14a67e5d1520bf.zip", "c9572672d1045594448068079b34c350"],
        "13": ["https://github.com/supremegamers/vendor_google_proprietary_ndk_translation-prebuilt/archive/a090003c60df53a9eadb2df09bd4fd2fa86ea629.zip", "e6f0d9fc28ebc427b59a3942a9a4ffc0"]
    }
    dl_file_name = "libndktranslation.zip"
    extract_to = "/tmp/libndkunpack"
    apply_props = {
        "ro.product.cpu.abilist": "x86_64,x86,armeabi-v7a,armeabi,arm64-v8a",
        "ro.product.cpu.abilist32": "x86,armeabi-v7a,armeabi",
        "ro.product.cpu.abilist64": "x86_64,arm64-v8a",
        "ro.dalvik.vm.native.bridge": "libndk_translation.so",
        "ro.enable.native.bridge.exec": "1",
        "ro.vendor.enable.native.bridge.exec": "1",
        "ro.vendor.enable.native.bridge.exec64": "1",
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
        self.dl_link = self.dl_links[android_version][0]
        self.act_md5 = self.dl_links[android_version][1]

    def copy(self):
        Logger.info("Copying libndk library files ...")
        name = re.findall("([a-zA-Z0-9]+)\.zip", self.dl_link)[0]
        shutil.copytree(os.path.join(self.extract_to, "vendor_google_proprietary_ndk_translation-prebuilt-" + name,
                        "prebuilts"), os.path.join(self.copy_dir, self.partition), dirs_exist_ok=True)