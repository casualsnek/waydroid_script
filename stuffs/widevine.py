import os
import re
import shutil
from stuffs.general import General
from tools.helper import host, run
from tools.logger import Logger


class Widevine(General):
    partition = "vendor"
    dl_links = {
        "x86": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/94c9ee172e3d78fecc81863f50a59e3646f7a2bd.zip", "a31f325453c5d239c21ecab8cfdbd878"],
        "x86_64": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/94c9ee172e3d78fecc81863f50a59e3646f7a2bd.zip", "a31f325453c5d239c21ecab8cfdbd878"],
        "armeabi-v7a": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/a1a19361d36311bee042da8cf4ced798d2c76d98.zip", "fed6898b5cfd2a908cb134df97802554"],
        "arm64-v8a": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/a1a19361d36311bee042da8cf4ced798d2c76d98.zip", "fed6898b5cfd2a908cb134df97802554"]
    }
    machine = host()
    dl_link = dl_links[machine[0]][0]
    act_md5 = dl_links[machine[0]][1]
    dl_file_name = "widevine.zip"
    extract_to = "/tmp/widevineunpack"
    files = [
            "bin/hw/*widevine",
            "bin/move_widevine_data.sh",
            "etc/init/*widevine.rc",
            "etc/vintf/manifest/*widevine.xml",
            "lib/libwvhidl.so",
            "lib/mediadrm",
            "lib64/mediadrm"
        ]

    def copy(self):
        run(["chmod", "+x", self.extract_to, "-R"])
        name = re.findall("([a-zA-Z0-9]+)\.zip", self.dl_link)[0]
        Logger.info("Copying widevine library files ...")
        shutil.copytree(os.path.join(self.extract_to, "vendor_google_proprietary_widevine-prebuilt-"+name,
                        "prebuilts"), os.path.join(self.copy_dir, self.partition), dirs_exist_ok=True)
