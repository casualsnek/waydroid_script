import os
import shutil
from stuffs.general import General

class HideStatusBar(General):
    dl_link = "https://github.com/ayasa520/hide-status-bar/releases/download/v0.0.1/app-release.apk"
    partition = "system"
    dl_file_name = "hidestatusbar.apk"
    act_md5 = "ae6c4cc567d6f3de77068e54e43818e2"
    files = [
            "product/overlay/"+dl_file_name
        ]
    
    def copy(self):
        rro_dir = os.path.join(self.copy_dir, self.partition, "product", "overlay")
        if not os.path.exists(rro_dir):
            os.makedirs(rro_dir)
        shutil.copyfile(self.download_loc, os.path.join(rro_dir, "hidestatusbar.apk"))
    
    def skip_extract(self):
        return True