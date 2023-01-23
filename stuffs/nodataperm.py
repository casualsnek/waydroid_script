import os
import shutil
from stuffs.general import General
from tools.helper import run
from tools.logger import Logger

class Nodataperm(General):
    dl_link = "https://github.com/ayasa520/hack_full_data_permission/archive/refs/heads/main.zip"
    dl_file_name = "nodataperm.zip"
    extract_to = "/tmp/nodataperm"
    act_md5 = "eafd7b0986f3edaebaf1dd89f19d49bf"
    partition = "system"

    def copy(self):
        extract_path = os.path.join(self.extract_to, "hack_full_data_permission-main")
        os.chmod(os.path.join(extract_path, "framework", "services.jar"), 0o644)
        os.chmod(os.path.join(extract_path, "etc", "nodataperm.sh"), 0o755)
        os.chmod(os.path.join(extract_path, "etc", "init", "nodataperm.rc"), 0o755)
        Logger.info("Copying widevine library files ...")
        shutil.copytree(extract_path, os.path.join(self.copy_dir, self.partition), dirs_exist_ok=True)
