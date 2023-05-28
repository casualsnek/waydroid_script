import os
import shutil
from stuff.general import General
from tools.logger import Logger


class MicroG(General):
    id = "MicroG"
    partition = "system"
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
    priv_apps = ["com.google.android.gms", "com.android.vending"]
    dl_links = {
        "Standard": [
            "https://github.com/ayasa520/MinMicroG/releases/download/latest/MinMicroG-Standard-2.11.1-20230429100529.zip",
            "0fe332a9caa3fbb294f2e2b50f720c6b"
        ],
        "NoGoolag": [
            "https://github.com/ayasa520/MinMicroG/releases/download/latest/MinMicroG-NoGoolag-2.11.1-20230429100545.zip",
            "ff920f33f4c874eeae4c0444be427c68"
        ],
        "UNLP": [
            "https://github.com/ayasa520/MinMicroG/releases/download/latest/MinMicroG-UNLP-2.11.1-20230429100555.zip",
            "6136b383153c2a6797d14fb4d7ca3f97"
        ],
        "Minimal": [
            "https://github.com/ayasa520/MinMicroG/releases/download/latest/MinMicroG-Minimal-2.11.1-20230429100521.zip"
            "afb87eb64e7749cfd72c4760d85849da"
        ],
        "MinimalIAP": [
            "https://github.com/ayasa520/MinMicroG/releases/download/latest/MinMicroG-MinimalIAP-2.11.1-20230429100556.zip"
            "cc071f4f776cbc16c4c1f707aff1f7fa"
        ]
    }
    dl_link = ...
    act_md5 = ...
    dl_file_name = ...
    sdk = ...
    extract_to = "/tmp/microg/extract"
    rc_content = '''
on property:sys.boot_completed=1
    start microg_service

service microg_service /system/bin/sh /system/bin/npem
    user root
    group root
    oneshot
    '''
    files = [
        "priv-app/GoogleBackupTransport",
        "priv-app/MicroGUNLP",
        "priv-app/MicroGGMSCore",
        "priv-app/MicroGGMSCore/lib/x86_64/libmapbox-gl.so",
        "priv-app/MicroGGMSCore/lib/x86_64/libconscrypt_gmscore_jni.so",
        "priv-app/MicroGGMSCore/lib/x86_64/libcronet.102.0.5005.125.so",
        "priv-app/PatchPhonesky",
        "priv-app/PatchPhonesky/lib/x86_64/libempty_x86_64.so",
        "priv-app/AuroraServices",
        "bin/npem",
        "app/GoogleCalendarSyncAdapter",
        "app/NominatimNLPBackend",
        "app/MicroGGSFProxy",
        "app/LocalGSMNLPBackend",
        "app/DejaVuNLPBackend",
        "app/MozillaUnifiedNLPBackend",
        "app/AppleNLPBackend",
        "app/AuroraDroid",
        "app/LocalWiFiNLPBackend",
        "app/GoogleContactsSyncAdapter",
        "app/MicroGGSFProxy/MicroGGSFProxy",
        "framework/com.google.widevine.software.drm.jar",
        "framework/com.google.android.media.effects.jar",
        "framework/com.google.android.maps.jar",
        "lib64/libjni_keyboarddecoder.so",
        "lib64/libjni_latinimegoogle.so",
        "etc/default-permissions/microg-permissions.xml",
        "etc/default-permissions/microg-permissions-unlp.xml",
        "etc/default-permissions/gsync.xml",
        "etc/sysconfig/nogoolag.xml",
        "etc/sysconfig/nogoolag-unlp.xml",
        "etc/init/microg.rc",
        "etc/permissions/com.google.android.backuptransport.xml",
        "etc/permissions/com.android.vending.xml",
        "etc/permissions/foss-permissions.xml",
        "etc/permissions/com.google.android.gms.xml",
        "etc/permissions/com.aurora.services.xml",
        "etc/permissions/com.google.android.maps.xml",
        "etc/permissions/com.google.widevine.software.drm.xml",
        "etc/permissions/com.google.android.media.effects.xml",
        "lib/libjni_keyboarddecoder.so",
        "lib/libjni_latinimegoogle.so",
    ]

    def __init__(self, android_version="11", variant="Standard") -> None:
        super().__init__()
        self.dl_link = self.dl_links[variant][0]
        self.act_md5 = self.dl_links[variant][1]
        self.id = self.id+f"-{variant}"
        self.dl_file_name = f'MinMicroG-{variant}.zip'
        if android_version == "11":
            self.sdk = 30
        elif android_version == "13":
            self.sdk = 33

    def copy(self):
        Logger.info("Copying libs and apks...")
        dst_dir = os.path.join(self.copy_dir, self.partition)
        src_dir = os.path.join(self.extract_to, "system")
        if "arm" in self.arch[0]:
            sub_arch = "arm"
        else:
            sub_arch = "x86"
        if 64 == self.arch[1]:
            arch = f"{sub_arch}{'' if sub_arch=='arm' else '_'}64"
        for root, dirs, files in os.walk(src_dir):
            flag = False
            dir_name = os.path.basename(root)
            # 遍历文件
            if dir_name.startswith('-') and dir_name.endswith('-'):
                archs, sdks = [], []
                for i in dir_name.split("-"):
                    if i.isdigit():
                        sdks.append(i)
                    elif i:
                        archs.append(i)
                if len(archs) != 0 and arch not in archs and sub_arch not in archs or len(sdks) != 0 and str(self.sdk) not in sdks:
                    continue
                else:
                    flag = True

            for file in files:
                src_file_path = os.path.join(root, file)
                if not flag:
                    dst_file_path = os.path.join(dst_dir, os.path.relpath(
                        src_file_path, src_dir))
                else:
                    dst_file_path = os.path.join(dst_dir, os.path.relpath(
                        os.path.join(os.path.dirname(root), file), src_dir))
                if not os.path.exists(os.path.dirname(dst_file_path)):
                    os.makedirs(os.path.dirname(dst_file_path))
                # Logger.info(f"{src_file_path} -> {dst_file_path}")
                shutil.copy2(src_file_path, dst_file_path)
                if os.path.splitext(dst_file_path)[1].lower() == ".apk":
                    self.extract_app_lib(dst_file_path)

        rc_dir = os.path.join(dst_dir, "etc/init/microg.rc")
        if not os.path.exists(os.path.dirname(rc_dir)):
            os.makedirs(os.path.dirname(rc_dir))
        with open(rc_dir, "w") as f:
            f.write(self.rc_content)

    def extra2(self):
        system_dir = os.path.join(self.copy_dir, self.partition)
        files = [key.split("_")[0] for key in self.fdroid_repo_apks.keys()]
        files += [key.split("-")[0] for key in self.microg_apks.keys()]
        for f in files:
            if f in self.priv_apps:
                file = os.path.join(system_dir, "priv-app", f)
            else:
                file = os.path.join(system_dir, "app", f)
            if os.path.isdir(file):
                shutil.rmtree(file)
            elif os.path.isfile(file):
                os.remove(file)
