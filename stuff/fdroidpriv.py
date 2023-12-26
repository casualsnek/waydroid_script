import os
import shutil
from stuff.general import General


class FDroidPriv(General):
    id = "fdroid priv"
    dl_links = {"11": ["https://f-droid.org/repo/org.fdroid.fdroid.privileged.ota_2130.zip",
                       "6242cab56d197d80c598593a46da62e4"]}
    partition = "system"
    dl_file_name = "org.fdroid.fdroid.privileged.ota_2130.zip"
    dl_link = ...
    act_md5 = ...
    extract_to = "/tmp/fdroid_ota_2130"
    files = [
        "app/F-Droid.apk"
        "app/F-Droid/F-Droid.apk"
        "etc/permissions/permissions_org.fdroid.fdroid.privileged.xml"
        "priv-app/F-DroidPrivilegedExtension.apk"
        "priv-app/F-DroidPrivilegedExtension/F-DroidPrivilegedExtension.apk"
    ]
    file_map = {
      "permissions_org.fdroid.fdroid.privileged.xml": "etc/permissions/permissions_org.fdroid.fdroid.privileged.xml",
      "F-Droid.apk": "app/F-Droid/F-Droid.apk",
      "F-DroidPrivilegedExtension.apk": "priv-app/F-DroidPrivilegedExtension/F-DroidPrivilegedExtension.apk",
    }
    def __init__(self, android_version="11") -> None:
        super().__init__()
        self.dl_link = self.dl_links[android_version][0]
        self.act_md5 = self.dl_links[android_version][1]

    def copy(self):
        for f, d in self.file_map.items():
            rro_file = os.path.join(
                self.copy_dir, self.partition, d)
            rro_dir = os.path.dirname(rro_file)
            if not os.path.exists(rro_dir):
                os.makedirs(rro_dir)
            shutil.copyfile(os.path.join(self.extract_to, f), rro_file)

