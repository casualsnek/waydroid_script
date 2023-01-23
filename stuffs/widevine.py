import os
import shutil
from stuffs.general import General
from tools.helper import run
from tools.logger import Logger


class Widevine(General):
    partition = "vendor"
    dl_link = "https://codeload.github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/zip/94c9ee172e3d78fecc81863f50a59e3646f7a2bd"
    dl_file_name = "widevine.zip"
    extract_to = "/tmp/widevineunpack"
    act_md5 = "a31f325453c5d239c21ecab8cfdbd878"

    def download(self):
        Logger.info("Downloading widevine to {} now .....".format(self.download_loc))
        super().download()

    def copy(self):
        run(["chmod", "+x", self.extract_to, "-R"])
        Logger.info("Copying widevine library files ...")
        shutil.copytree(os.path.join(self.extract_to, "vendor_google_proprietary_widevine-prebuilt-94c9ee172e3d78fecc81863f50a59e3646f7a2bd",
                        "prebuilts"), os.path.join(self.copy_dir, self.partition), dirs_exist_ok=True)