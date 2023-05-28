import gzip
import os
import shutil
from stuff.general import General
from tools.logger import Logger
from tools import container


class Nodataperm(General):
    id = "nodataperm"
    dl_links = {
        "11": ["https://github.com/ayasa520/hack_full_data_permission/archive/refs/heads/main.zip",
               "eafd7b0986f3edaebaf1dd89f19d49bf"],
        "13": ["", ""]
    }
    dl_file_name = "nodataperm.zip"
    extract_to = "/tmp/nodataperm"
    dl_link = ...
    act_md5 = ...
    partition = "system"
    files = [
        "etc/nodataperm.sh",
        "etc/init/nodataperm.rc",
        "framework/services.jar"
    ]

    def __init__(self, android_version="11") -> None:
        super().__init__()
        self.dl_link = self.dl_links[android_version][0]
        self.act_md5 = self.dl_links[android_version][1]

    def copy(self):
        extract_path = os.path.join(
            self.extract_to, "hack_full_data_permission-main")
        if not container.use_overlayfs():
            services_jar = os.path.join(
                self.copy_dir, self.partition, "framework", "services.jar")
            gz_filename = services_jar+".gz"
            with gzip.open(gz_filename, 'wb') as f_gz:
                with open(services_jar, "rb") as f:
                    f_gz.write(f.read())
        Logger.info("Copying widevine library files ...")
        shutil.copytree(extract_path, os.path.join(
            self.copy_dir, self.partition), dirs_exist_ok=True)

    def extra2(self):
        if not container.use_overlayfs():
            services_jar = os.path.join(
                self.copy_dir, self.partition, "framework", "services.jar")
            gz_filename = services_jar+".gz"
            with gzip.GzipFile(gz_filename) as f_gz:
                with open(services_jar, "wb") as f:
                    f.writelines(f_gz)
