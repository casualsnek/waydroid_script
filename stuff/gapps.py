import os
import shutil
from stuff.general import General
from tools.helper import run


class Gapps(General):
    id = ...
    partition = "system"
    dl_links = {
        "11": {
            "x86_64": ["https://sourceforge.net/projects/opengapps/files/x86_64/20220503/open_gapps-x86_64-11.0-pico-20220503.zip", "5a6d242be34ad1acf92899c7732afa1b"],
            "x86": ["https://sourceforge.net/projects/opengapps/files/x86/20220503/open_gapps-x86-11.0-pico-20220503.zip", "efda4943076016d00b40e0874b12ddd3"],
            "arm64-v8a": ["https://sourceforge.net/projects/opengapps/files/arm64/20220503/open_gapps-arm64-11.0-pico-20220503.zip", "7790055d34bbfc6fe610b0cd263a7add"],
            "armeabi-v7a": ["https://sourceforge.net/projects/opengapps/files/arm/20220215/open_gapps-arm-11.0-pico-20220215.zip", "8719519fa32ae83a62621c6056d32814"]
        },
        "13": {
            "x86_64": ["https://github.com/Howard20181/MindTheGappsBuilder/releases/download/20230323/MindTheGapps-13.0.0-x86_64-20230323.zip", "aba427be1ddd0963121c87a4eda80299"],
            "x86": ["https://github.com/Howard20181/MindTheGappsBuilder/releases/download/20230323/MindTheGapps-13.0.0-x86-20230323.zip", "f02d2f1a3f0a084f13ab4c1b58ad7554"],
            "arm64-v8a": ["https://github.com/Howard20181/MindTheGappsBuilder/releases/download/20230323/MindTheGapps-13.0.0-arm64-20230323.zip", "18484a5622eeccffcea2b43205655d8a"],
            "armeabi-v7a": ["https://github.com/Howard20181/MindTheGappsBuilder/releases/download/20230323/MindTheGapps-13.0.0-arm-20230323.zip", "e4c00a7eb1e4dfca0fc6a3e447710264"]
        }
    }
    android_version = ...
    dl_link = ...
    act_md5 = ...
    dl_file_name = "gapps.zip"
    extract_to = "/tmp/gapps/extract"
    non_apks = [
        "defaultetc-common.tar.lz",
        "defaultframework-common.tar.lz",
        "googlepixelconfig-common.tar.lz",
        "vending-common.tar.lz"
    ]
    skip = [
        "setupwizarddefault-x86_64.tar.lz",
        "setupwizardtablet-x86_64.tar.lz"
    ]
    files = [
        "etc/default-permissions/default-permissions.xml",
        "etc/default-permissions/opengapps-permissions-q.xml",
        "etc/permissions/com.google.android.maps.xml",
        "etc/permissions/com.google.android.media.effects.xml",
        "etc/permissions/privapp-permissions-google.xml",
        "etc/permissions/split-permissions-google.xml",
        "etc/preferred-apps/google.xml",
        "etc/sysconfig/google.xml",
        "etc/sysconfig/google_build.xml",
        "etc/sysconfig/google_exclusives_enable.xml",
        "etc/sysconfig/google-hiddenapi-package-whitelist.xml",
        "framework/com.google.android.maps.jar",
        "framework/com.google.android.media.effects.jar",
        "priv-app/AndroidMigratePrebuilt",
        "priv-app/GoogleExtServices",
        "priv-app/GoogleRestore",
        "priv-app/CarrierSetup",
        "priv-app/GoogleExtShared",
        "priv-app/GoogleServicesFramework",
        "priv-app/ConfigUpdater",
        "priv-app/GoogleFeedback",
        "priv-app/Phonesky",
        "priv-app/GoogleBackupTransport",
        "priv-app/GoogleOneTimeInitializer",
        "priv-app/PrebuiltGmsCore",
        "priv-app/GoogleContactsSyncAdapter",
        "priv-app/GooglePartnerSetup",
        "product/overlay/PlayStoreOverlay.apk",
        "product/overlay/GmsOverlay.apk.apk",
        "product/overlay/GmsSettingsProviderOverlay.apk",
        "system_ext/etc/permissions/privapp-permissions-google-system-ext.xml",
        "system_ext/priv-app/GoogleFeedback",
        "system_ext/priv-app/GoogleServicesFramework",
        "system_ext/priv-app/SetupWizard",
        "product/priv-app/GmsCore",
        "product/priv-app/AndroidAutoStub",
        "product/priv-app/GoogleRestore",
        "product/priv-app/Phonesky",
        "product/priv-app/Velvet",
        "product/priv-app/GooglePartnerSetup",
        "product/app/GoogleCalendarSyncAdapter",
        "product/app/PrebuiltExchange3Google",
        "product/app/GoogleContactsSyncAdapter",
        "product/framework/com.google.android.dialer.support.jar",
        "product/lib64/libjni_latinimegoogle.so",
        "product/etc/default-permissions/default-permissions-google.xml",
        "product/etc/default-permissions/default-permissions-mtg.xml",
        "product/etc/sysconfig/google.xml",
        "product/etc/sysconfig/d2d_cable_migration_feature.xml",
        "product/etc/sysconfig/google-hiddenapi-package-allowlist.xml",
        "product/etc/sysconfig/google_build.xml",
        "product/etc/permissions/privapp-permissions-google-product.xml",
        "product/etc/permissions/com.google.android.dialer.support.xml",
        "product/etc/security/fsverity/gms_fsverity_cert.der",
        "product/lib/libjni_latinimegoogle.so",
    ]

    def __init__(self, android_version="11") -> None:
        super().__init__()
        self.android_version = android_version
        self.dl_link = self.dl_links[android_version][self.arch[0]][0]
        self.act_md5 = self.dl_links[android_version][self.arch[0]][1]
        if android_version == "11":
            self.id = "OpenGapps"
        else:
            self.id = "MindTheGapps"

    def copy(self):
        if self.android_version == "11":
            return self.copy_11()
        elif self.android_version == "13":
            return self.copy_13()

    def copy_11(self):
        if not os.path.exists(self.extract_to):
            os.makedirs(self.extract_to)
        if not os.path.exists(os.path.join(self.extract_to, "appunpack")):
            os.makedirs(os.path.join(self.extract_to, "appunpack"))

        for lz_file in os.listdir(os.path.join(self.extract_to, "Core")):
            for d in os.listdir(os.path.join(self.extract_to, "appunpack")):
                shutil.rmtree(os.path.join(self.extract_to, "appunpack", d))
            if lz_file not in self.skip:
                if lz_file not in self.non_apks:
                    print("    Processing app package : " +
                          os.path.join(self.extract_to, "Core", lz_file))
                    run(["tar", "--lzip", "-xvf", os.path.join(self.extract_to, "Core",
                        lz_file), "-C", os.path.join(self.extract_to, "appunpack")])
                    app_name = os.listdir(os.path.join(
                        self.extract_to, "appunpack"))[0]
                    xx_dpi = os.listdir(os.path.join(
                        self.extract_to, "appunpack", app_name))[0]
                    app_priv = os.listdir(os.path.join(
                        self.extract_to, "appunpack", app_name, "nodpi"))[0]
                    app_src_dir = os.path.join(
                        self.extract_to, "appunpack", app_name, xx_dpi, app_priv)
                    for app in os.listdir(app_src_dir):
                        shutil.copytree(os.path.join(app_src_dir, app), os.path.join(
                            self.copy_dir, self.partition, "priv-app", app), dirs_exist_ok=True)
                        for f in os.listdir(os.path.join(self.copy_dir, self.partition, "priv-app", app)):
                            dst_file_path = os.path.join(os.path.join(
                                self.copy_dir, self.partition, "priv-app", app), f)
                            if os.path.splitext(dst_file_path)[1].lower() == ".apk":
                                self.extract_app_lib(dst_file_path)
                else:
                    print("    Processing extra package : " +
                          os.path.join(self.extract_to, "Core", lz_file))
                    run(["tar", "--lzip", "-xvf", os.path.join(self.extract_to, "Core",
                        lz_file), "-C", os.path.join(self.extract_to, "appunpack")])
                    app_name = os.listdir(os.path.join(
                        self.extract_to, "appunpack"))[0]
                    common_content_dirs = os.listdir(os.path.join(
                        self.extract_to, "appunpack", app_name, "common"))
                    for ccdir in common_content_dirs:
                        shutil.copytree(os.path.join(self.extract_to, "appunpack", app_name, "common", ccdir), os.path.join(
                            self.copy_dir, self.partition, ccdir), dirs_exist_ok=True)

    def copy_13(self):
        src_dir = os.path.join(self.extract_to, "system")
        dst_dir = os.path.join(self.copy_dir, self.partition)
        for root, dirs, files in os.walk(src_dir):
            dir_name = os.path.basename(root)
            # 遍历文件
            for file in files:
                src_file_path = os.path.join(root, file)
                dst_file_path = os.path.join(dst_dir, os.path.relpath(
                        src_file_path, src_dir))
                if not os.path.exists(os.path.dirname(dst_file_path)):
                    os.makedirs(os.path.dirname(dst_file_path))
                # Logger.info(f"{src_file_path} -> {dst_file_path}")
                shutil.copy2(src_file_path, dst_file_path)
                if os.path.splitext(dst_file_path)[1].lower() == ".apk":
                    self.extract_app_lib(dst_file_path)
