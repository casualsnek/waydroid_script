import os
import re
import shutil
from stuffs.general import General
from tools.helper import run
from tools.logger import Logger


class Houdini(General):
    partition = "system"
    dl_link =  "https://github.com/supremegamers/vendor_intel_proprietary_houdini/archive/81f2a51ef539a35aead396ab7fce2adf89f46e88.zip"
    act_md5 = "fbff756612b4144797fbc99eadcb6653"
    dl_file_name = "libhoudini.zip"
    extract_to = "/tmp/houdiniunpack"
    init_rc_component = """
on early-init
    mount -t binfmt_misc binfmt_misc /proc/sys/fs/binfmt_misc

on property:ro.enable.native.bridge.exec=1
    exec -- /system/bin/sh -c "echo ':arm_exe:M::\\\\x7f\\\\x45\\\\x4c\\\\x46\\\\x01\\\\x01\\\\x01\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x02\\\\x00\\\\x28::/system/bin/houdini:P' > /proc/sys/fs/binfmt_misc/register"
    exec -- /system/bin/sh -c "echo ':arm_dyn:M::\\\\x7f\\\\x45\\\\x4c\\\\x46\\\\x01\\\\x01\\\\x01\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x03\\\\x00\\\\x28::/system/bin/houdini:P' >> /proc/sys/fs/binfmt_misc/register"
    exec -- /system/bin/sh -c "echo ':arm64_exe:M::\\\\x7f\\\\x45\\\\x4c\\\\x46\\\\x02\\\\x01\\\\x01\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x02\\\\x00\\\\xb7::/system/bin/houdini64:P' >> /proc/sys/fs/binfmt_misc/register"
    exec -- /system/bin/sh -c "echo ':arm64_dyn:M::\\\\x7f\\\\x45\\\\x4c\\\\x46\\\\x02\\\\x01\\\\x01\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x03\\\\x00\\\\xb7::/system/bin/houdini64:P' >> /proc/sys/fs/binfmt_misc/register"
"""
    apply_props = {
        "ro.product.cpu.abilist": "x86_64,x86,arm64-v8a,armeabi-v7a,armeabi",
        "ro.product.cpu.abilist32": "x86,armeabi-v7a,armeabi",
        "ro.product.cpu.abilist64": "x86_64,arm64-v8a",
        "ro.dalvik.vm.native.bridge": "libhoudini.so",
        "ro.enable.native.bridge.exec": "1",
        "ro.dalvik.vm.isa.arm": "x86",
        "ro.dalvik.vm.isa.arm64": "x86_64"
    }

    def download(self):
        Logger.info("Downloading libhoudini to {}now .....".format(self.download_loc))
        super().download()

    def copy(self):
        run(["chmod", "+x", self.extract_to, "-R"])
        Logger.info("Copying libhoudini library files ...")
        name = re.findall("([a-zA-Z0-9]+)\.zip", self.dl_link)[0]
        shutil.copytree(os.path.join(self.extract_to, "vendor_intel_proprietary_houdini-" + name,
                        "prebuilts"), os.path.join(self.copy_dir, self.partition), dirs_exist_ok=True)
        init_path = os.path.join(self.copy_dir, self.partition, "etc", "init", "houdini.rc")
        if not os.path.isfile(init_path):
            os.makedirs(os.path.dirname(init_path), exist_ok=True)
        with open(init_path, "w") as initfile:
            initfile.write(self.init_rc_component)        
