from os import path, makedirs
import shutil
from stuffs.general import General
from tools.helper import run
from tools.logger import Logger

class Ndk(General):
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
    
    def download(self):
        Logger.info("Downloading libndk to {} now .....".format(self.download_loc))
        super().download()

    def copy(self):
        run(["chmod", "+x", self.extract_to, "-R"])
        Logger.info("Copying libndk library files ...")
        archive_url, commit_sha = path.split(path.splitext(self.dl_link)[0])
        zipped_basepath, _ = path.split(archive_url)
        prebuilts_sourcedir = path.join(
            self.extract_to,
            f"{path.basename(zipped_basepath)}-{commit_sha}",
            "prebuilts")
        shutil.copytree(
            prebuilts_sourcedir,
            path.join(self.copy_dir, self.partition),
            dirs_exist_ok=True)

        init_path = path.join(self.copy_dir, self.partition, "etc", "init", "libndk.rc")
        if not path.isfile(init_path):
            makedirs(path.dirname(init_path), exist_ok=True)
        with open(init_path, "w") as initfile:
            initfile.write(self.init_rc_component)