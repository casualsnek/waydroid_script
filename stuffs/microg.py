import os
import shutil
from time import sleep
from stuffs.general import General
from tools.helper import get_download_dir, host, run
from aapt2 import aapt
from tools import container
from tools.logger import Logger


class MicroG(General):
    partition = "system"
    main_arch = host()[0]
    sub_arch = "x86" if main_arch == "x86_64" else "armeabi-v7a" if main_arch == "arm64-v8a" else ""
    fdroid = "https://f-droid.org/repo/"
    microg="https://microg.org/fdroid/repo/"
    fdroid_repo_apks = {
        "com.aurora.store_41.apk": "9e6c79aefde3f0bbfedf671a2d73d1be",
        "com.etesync.syncadapter_20300.apk": "997d6de7d41c454d39fc22cd7d8fc3c2",
        "com.aurora.adroid_8.apk": "0010bf93f02c2d18daf9e767035fefc5",
        "org.fdroid.fdroid.privileged_2130.apk": "b04353155aceb36207a206d6dd14ba6a",
        "org.microg.nlp.backend.ichnaea_20036.apk": "0b3cb65f8458d1a5802737c7392df903",
        "org.microg.nlp.backend.nominatim_20042.apk": "88e7397cbb9e5c71c8687d3681a23383",
    }
    microg_apks= {
        "com.google.android.gms-223616054.apk": "a945481ca5d33a03bc0f9418263c3228",
        "com.google.android.gsf-8.apk": "b2b4ea3642df6158e14689a4b2a246d4",
        "com.android.vending-22.apk": "6815d191433ffcd8fa65923d5b0b0573",
        "org.microg.gms.droidguard-14.apk": "4734b41c1a6bc34a541053ddde7a0f8e"
    }

    def skip_extract(self):
        return True

    def download(self):
        for apk, md5 in self.fdroid_repo_apks.items():
            self.dl_link = self.fdroid+apk
            self.act_md5 = md5
            self.dl_file_name = apk
            super().download()
        for apk, md5 in self.microg_apks.items():
            self.dl_link = self.microg+apk
            self.act_md5 = md5
            self.dl_file_name = apk
            super().download()

    def generate_permissions(self):
        permissions = "<permissions>"
        download_dir = get_download_dir()
        for apk in {**self.fdroid_repo_apks, **self.microg_apks}.keys():
            splitor = "_" if apk in self.fdroid_repo_apks.keys() else "-"
            package = apk.split(splitor)[0]
            permissions += '\n\t<privapp-permissions package="{}">\n'.format(package)
            permission_list = aapt.get_apk_info(os.path.join(download_dir,apk))["permissions"]
            permissions += "\n".join(['\t\t<permission name="{}"/>'.format(permission) for permission in permission_list])
            permissions += "\n\t</privapp-permissions>"
        return permissions

    def copy(self):
        Logger.info("Copying MicroG and other files")
        priv_apps = ["com.google.android.gms", "com.android.vending"]
        for apk in {**self.fdroid_repo_apks, **self.microg_apks}.keys():
            splitor = "_" if apk in self.fdroid_repo_apks.keys() else "-"
            package = apk.split(splitor)[0]
            download_dir = get_download_dir()
            apk_dir = "app" if package not in priv_apps else "priv-app"
            if not os.path.exists(os.path.join(self.copy_dir, self.partition, apk_dir, package)):
                os.makedirs(os.path.join(self.copy_dir, self.partition, apk_dir, package))
            shutil.copyfile(os.path.join(download_dir, apk),
                os.path.join(self.copy_dir, self.partition, apk_dir, package, apk))
        permissions = self.generate_permissions()
        permission_dir = os.path.join(self.copy_dir, self.partition, "etc", "permissions")
        if not os.path.exists(permission_dir):
            os.makedirs(permission_dir)
        with open(os.path.join(permission_dir, "foss-permissions.xml"), "w") as f:
            f.write(permissions)
    
    def extra2(self):
        index = 0
        while not container.is_running():
            list = ["\\", "|", "/", "—"]
            sleep(0.5)
            print("\r\tPlease start WayDroid for further setup {}".format(list[index%4]), end="")
            index += 1
        sleep(5)
        print()
        Logger.info("Signature spoofing")
        run("waydroid shell pm grant com.google.android.gms android.permission.FAKE_PACKAGE_SIGNATURE".split())
        run("waydroid shell pm grant com.android.vending android.permission.FAKE_PACKAGE_SIGNATURE".split())
