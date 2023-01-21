import os
import shutil
from stuffs.general import General

class Smartdock(General):
    dl_link = "https://github.com/ayasa520/smartdock/releases/download/v1.9.6/smartdock.zip"
    partition = "system"
    extract_to = "/tmp/smartdockunpack"
    dl_file_name = "smartdock.zip"
    act_md5 = "ad0cc5e023ac6ee97e7b013b9b0defee"

    def copy(self):
        if not os.path.exists(os.path.join(self.copy_dir, self.partition, "priv-app", "SmartDock")):
            os.makedirs(os.path.join(self.copy_dir, self.partition, "priv-app", "SmartDock"))
        shutil.copyfile(os.path.join(self.extract_to, "app-release.apk"),
                        os.path.join(self.copy_dir, self.partition, "priv-app", "SmartDock", "smartdock.apk"))
        shutil.copyfile(os.path.join(self.extract_to, "permissions_cu.axel.smartdock.xml"),
                        os.path.join(self.copy_dir, self.partition, "etc", "permissions", "permissions_cu.axel.smartdock.xml"))

    def extra(self):
        return super().extra()
