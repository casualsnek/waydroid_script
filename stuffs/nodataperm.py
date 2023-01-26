import gzip
import os
import shutil
from stuffs.general import General
from tools.helper import run
from tools.logger import Logger
from tools import container

class Nodataperm(General):
    dl_link = "https://github.com/ayasa520/hack_full_data_permission/archive/refs/heads/main.zip"
    dl_file_name = "nodataperm.zip"
    extract_to = "/tmp/nodataperm"
    act_md5 = "eafd7b0986f3edaebaf1dd89f19d49bf"
    partition = "system"
    files = [
            "etc/nodataperm.sh",
            "etc/init/nodataperm.rc",
            "framework/services.jar"
        ]

    def copy(self):
        extract_path = os.path.join(self.extract_to, "hack_full_data_permission-main")
        if not container.use_overlayfs():
            services_jar = os.path.join(self.copy_dir, self.partition, "framework", "services.jar")
            gz_filename = services_jar+".gz"
            with gzip.open(gz_filename,'wb') as f_gz:
                with open(services_jar, "rb") as f:
                    f_gz.write(f.read())
        os.chmod(os.path.join(extract_path, "framework", "services.jar"), 0o644)
        os.chmod(os.path.join(extract_path, "etc", "nodataperm.sh"), 0o755)
        os.chmod(os.path.join(extract_path, "etc", "init", "nodataperm.rc"), 0o755)
        Logger.info("Copying widevine library files ...")
        shutil.copytree(extract_path, os.path.join(self.copy_dir, self.partition), dirs_exist_ok=True)

    def extra3(self):
        if not container.use_overlayfs():               
            services_jar = os.path.join(self.copy_dir, self.partition, "framework", "services.jar")
            gz_filename = services_jar+".gz"       
            with gzip.GzipFile(gz_filename) as f_gz:
                with open(services_jar, "wb") as f:
                    f.writelines(f_gz)
