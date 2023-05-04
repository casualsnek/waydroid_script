import os
import shutil
from stuff.general import General


class HideStatusBar(General):
    id = "hide status bar"
    dl_links = {"11": ["https://github.com/ayasa520/hide-status-bar/releases/download/v0.0.1/app-release.apk",
                       "ae6c4cc567d6f3de77068e54e43818e2"]}
    partition = "system"
    dl_file_name = "hidestatusbar.apk"
    dl_link = ...
    act_md5 = ...
    files = [
        "product/overlay/"+dl_file_name
    ]
    def __init__(self, android_version="11") -> None:
        super().__init__()
        self.dl_link = self.dl_links[android_version][0]
        self.act_md5 = self.dl_links[android_version][1]

    def copy(self):
        rro_dir = os.path.join(
            self.copy_dir, self.partition, "product", "overlay")
        if not os.path.exists(rro_dir):
            os.makedirs(rro_dir)
        shutil.copyfile(self.download_loc, os.path.join(
            rro_dir, "hidestatusbar.apk"))

    def skip_extract(self):
        return True
