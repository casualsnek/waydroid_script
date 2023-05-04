import os
import re
import shutil
from stuff.general import General
from tools.logger import Logger


class Widevine(General):
    id = "widevine"
    partition = "vendor"
    dl_links = {
        # "x86": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/94c9ee172e3d78fecc81863f50a59e3646f7a2bd.zip", "a31f325453c5d239c21ecab8cfdbd878"],
        "x86_64": {
            "11": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/48d1076a570837be6cdce8252d5d143363e37cc1.zip",
                   "f587b8859f9071da4bca6cea1b9bed6a"],
            "13": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/a8524d608431573ef1c9313822d271f78728f9a6.zip",
                   "5c55df61da5c012b4e43746547ab730f"]
        },
        # "armeabi-v7a": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/a1a19361d36311bee042da8cf4ced798d2c76d98.zip", "fed6898b5cfd2a908cb134df97802554"],
        "arm64-v8a": {
            "11": ["https://github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/archive/a1a19361d36311bee042da8cf4ced798d2c76d98.zip",
                   "fed6898b5cfd2a908cb134df97802554"]
        }
    }
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

    def __init__(self, android_version) -> None:
        super().__init__()
        self.dl_link = self.dl_links[self.arch[0]][android_version][0]
        self.act_md5 = self.dl_links[self.arch[0]][android_version][1]

    def copy(self):
        name = re.findall("([a-zA-Z0-9]+)\.zip", self.dl_link)[0]
        Logger.info("Copying widevine library files ...")
        shutil.copytree(os.path.join(self.extract_to, "vendor_google_proprietary_widevine-prebuilt-"+name,
                        "prebuilts"), os.path.join(self.copy_dir, self.partition), dirs_exist_ok=True)
