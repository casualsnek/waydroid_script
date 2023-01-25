import os
import shutil
from time import sleep
from stuffs.general import General
from tools import container
from tools.helper import run

class Smartdock(General):
    dl_link = "https://github.com/ayasa520/smartdock/releases/download/v1.9.6/smartdock.zip"
    partition = "system"
    extract_to = "/tmp/smartdockunpack"
    dl_file_name = "smartdock.zip"
    act_md5 = "ad0cc5e023ac6ee97e7b013b9b0defee"
    apply_props = { "qemu.hw.mainkeys" : "1" }

    def copy(self):
        if not os.path.exists(os.path.join(self.copy_dir, self.partition, "priv-app", "SmartDock")):
            os.makedirs(os.path.join(self.copy_dir, self.partition, "priv-app", "SmartDock"))
        if not os.path.exists(os.path.join(self.copy_dir, self.partition, "etc", "permissions")):
            os.makedirs(os.path.join(self.copy_dir, self.partition, "etc", "permissions"))
        shutil.copyfile(os.path.join(self.extract_to, "app-release.apk"),
                        os.path.join(self.copy_dir, self.partition, "priv-app", "SmartDock", "smartdock.apk"))
        shutil.copyfile(os.path.join(self.extract_to, "permissions_cu.axel.smartdock.xml"),
                        os.path.join(self.copy_dir, self.partition, "etc", "permissions", "permissions_cu.axel.smartdock.xml"))

    def extra2(self):
        index = 0
        while not container.is_running():
            list = ["\\", "|", "/", "—"]
            sleep(0.5)
            print("\r\tPlease start WayDroid for further setup {}".format(list[index%4]), end="")
            index += 1
        sleep(5)
        if index != 0:
            print()
        run(["waydroid", "shell", "cmd", "package", "set-home-activity", "cu.axel.smartdock/.activities.LauncherActivity"])
