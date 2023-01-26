import glob
import os
import shutil
from stuffs.general import General
from tools.helper import run
from tools.logger import Logger

class Ndk(General):
    partition = "system"
    dl_link = "https://www.dropbox.com/s/eaf4dj3novwiccp/libndk_translation_Module-c6077f3398172c64f55aad7aab0e55fad9110cf3.zip?dl=1"
    dl_file_name = "libndktranslation.zip"
    extract_to = "/tmp/libndkunpack"
    act_md5 = "4456fc1002dc78e544e8d9721bb24398"
    apply_props = {
        "ro.product.cpu.abilist": "x86_64,x86,armeabi-v7a,armeabi,arm64-v8a",
        "ro.product.cpu.abilist32": "x86,armeabi-v7a,armeabi",
        "ro.product.cpu.abilist64": "x86_64,arm64-v8a",
        "ro.dalvik.vm.native.bridge": "libndk_translation.so",
        "ro.enable.native.bridge.exec": "1",
      #  "ro.ndk_translation.version": "0.2.2",
        "ro.dalvik.vm.isa.arm": "x86",
        "ro.dalvik.vm.isa.arm64": "x86_64"
    }
    init_rc_component = """
# Enable native bridge for target executables
on early-init
    mount binfmt_misc binfmt_misc /proc/sys/fs/binfmt_misc

on property:ro.enable.native.bridge.exec=1
    copy /system/etc/binfmt_misc/arm_exe /proc/sys/fs/binfmt_misc/register
    copy /system/etc/binfmt_misc/arm_dyn /proc/sys/fs/binfmt_misc/register
    copy /system/etc/binfmt_misc/arm64_exe /proc/sys/fs/binfmt_misc/register
    copy /system/etc/binfmt_misc/arm64_dyn /proc/sys/fs/binfmt_misc/register
"""
    files = [
            "bin/arm",
            "bin/arm64",
            "bin/ndk_translation_program_runner_binfmt_misc",
            "bin/ndk_translation_program_runner_binfmt_misc_arm64",
            "etc/binfmt_misc",
            "etc/ld.config.arm.txt",
            "etc/ld.config.arm64.txt",
            "etc/init/libndk.rc",
            "lib/arm",
            "lib64/arm64",
            "lib/libndk*",
            "lib64/libndk*"
        ]

    def copy(self):
        run(["chmod", "+x", self.extract_to, "-R"])
        Logger.info("Copying libndk library files ...")
        shutil.copytree(os.path.join(self.extract_to, "libndk_translation_Module-c6077f3398172c64f55aad7aab0e55fad9110cf3", "system"), os.path.join(self.copy_dir, self.partition), dirs_exist_ok=True)

        init_path = os.path.join(self.copy_dir, self.partition, "etc", "init", "libndk.rc")
        if not os.path.isfile(init_path):
            os.makedirs(os.path.dirname(init_path), exist_ok=True)
        with open(init_path, "w") as initfile:
            initfile.write(self.init_rc_component)
        