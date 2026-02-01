import os
import re
import shutil
from stuff.general import General
from tools.helper import backup, restore
from tools.logger import Logger
from tools import container


class Nodataperm(General):
    id = "nodataperm"
    dl_links = {
        "11": {
            "x86_64": [
                "https://github.com/ayasa520/hack_full_data_permission/archive/d4beab7780eb792059d33e77d865579c9ee41546.zip",
                "b0e3908ffcf5df8ea62f4929aa680f1a"
            ],
        },
        "13": {
            "x86_64": [
                "https://github.com/ayasa520/hack_full_data_permission/archive/d4beab7780eb792059d33e77d865579c9ee41546.zip",
                "b0e3908ffcf5df8ea62f4929aa680f1a"
            ],
        },
    }
    dl_file_name = "nodataperm.zip"
    extract_to = "/tmp/nodataperm"
    dl_link = None
    act_md5 = None
    partition = "system"
    files = [
        "etc/nodataperm.sh",
        "etc/init/nodataperm.rc",
        "framework/services.jar",
        "framework/services.jar.prof",
        "framework/services.jar.bprof",
    ]

    def __init__(self, android_version="11") -> None:
        super().__init__()
        print("ok")
        arch = self.arch[0]
        if android_version not in self.dl_links:
            raise KeyError(f"No download links for Android version '{android_version}'")
        if arch not in self.dl_links[android_version]:
            raise KeyError(f"No download links for architecture '{arch}' in Android version '{android_version}'")
        self.dl_link = self.dl_links[android_version][arch][0]
        self.act_md5 = self.dl_links[android_version][arch][1]

    def copy(self):
        name = re.findall(r"([a-zA-Z0-9]+)\.zip", self.dl_link)[0]
        extract_path = os.path.join(
            self.extract_to, f"hack_full_data_permission-{name}")
        if not container.use_overlayfs():
            services_jar = os.path.join(
                self.copy_dir, self.partition, "framework", "services.jar")
            services_jar_prof = os.path.join(
                self.copy_dir, self.partition, "framework", "services.jar.prof")
            services_jar_bprof = os.path.join(
                self.copy_dir, self.partition, "framework", "services.jar.bprof")
            backup(services_jar)
            backup(services_jar_prof)
            backup(services_jar_bprof)

        Logger.info(f"Copying {self.id} library files ...")
        shutil.copytree(extract_path, os.path.join(
            self.copy_dir, self.partition), dirs_exist_ok=True)

    def extra2(self):
        if not container.use_overlayfs():
            services_jar = os.path.join(
                self.copy_dir, self.partition, "framework", "services.jar")
            services_jar_prof = os.path.join(
                self.copy_dir, self.partition, "framework", "services.jar.prof")
            services_jar_bprof = os.path.join(
                self.copy_dir, self.partition, "framework", "services.jar.bprof")
            restore(services_jar)
            restore(services_jar_prof)
            restore(services_jar_bprof)
