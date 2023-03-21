import os
import shutil
from stuffs.general import General
from tools.helper import host, run

class Gapps(General):
    partition = "system"
    dl_links = {
            "x86_64": ["https://sourceforge.net/projects/opengapps/files/x86_64/20220503/open_gapps-x86_64-11.0-pico-20220503.zip", "5a6d242be34ad1acf92899c7732afa1b"],
            "x86": ["https://sourceforge.net/projects/opengapps/files/x86/20220503/open_gapps-x86-11.0-pico-20220503.zip", "efda4943076016d00b40e0874b12ddd3"],
            "arm64-v8a": ["https://sourceforge.net/projects/opengapps/files/arm64/20220503/open_gapps-arm64-11.0-pico-20220503.zip", "7790055d34bbfc6fe610b0cd263a7add"],
            "armeabi-v7a": ["https://sourceforge.net/projects/opengapps/files/arm/20220215/open_gapps-arm-11.0-pico-20220215.zip", "8719519fa32ae83a62621c6056d32814"]
        }
    arch = host()
    dl_link = dl_links[arch[0]][0]
    dl_file_name = "open_gapps.zip"
    act_md5 = dl_links[arch[0]][1]
    extract_to = "/tmp/ogapps/extract"
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
            "product/overlay/PlayStoreOverlay.apk"
        ]

    def copy(self):
        if not os.path.exists(self.extract_to):
            os.makedirs(self.extract_to)
        if not os.path.exists(os.path.join(self.extract_to, "appunpack")):
            os.makedirs(os.path.join(self.extract_to, "appunpack"))

        for lz_file in os.listdir(os.path.join(self.extract_to, "Core")):
            for d in os.listdir(os.path.join(self.extract_to, "appunpack")):
                shutil.rmtree(os.path.join(self.extract_to, "appunpack", d))
            if lz_file not in self.skip:
                if lz_file not in self.non_apks:
                    print("    Processing app package : "+os.path.join(self.extract_to, "Core", lz_file))
                    run(["tar", "--lzip", "-xvf", os.path.join(self.extract_to, "Core", lz_file), "-C", os.path.join(self.extract_to, "appunpack")])
                    app_name = os.listdir(os.path.join(self.extract_to, "appunpack"))[0]
                    xx_dpi = os.listdir(os.path.join(self.extract_to, "appunpack", app_name))[0]
                    app_priv = os.listdir(os.path.join(self.extract_to, "appunpack", app_name, "nodpi"))[0]
                    app_src_dir = os.path.join(self.extract_to, "appunpack", app_name, xx_dpi, app_priv)
                    for app in os.listdir(app_src_dir):
                        shutil.copytree(os.path.join(app_src_dir, app), os.path.join(self.copy_dir, self.partition, "priv-app", app), dirs_exist_ok=True)
                else:
                    print("    Processing extra package : "+os.path.join(self.extract_to, "Core", lz_file))
                    run(["tar", "--lzip", "-xvf", os.path.join(self.extract_to, "Core", lz_file), "-C", os.path.join(self.extract_to, "appunpack")])
                    app_name = os.listdir(os.path.join(self.extract_to, "appunpack"))[0]
                    common_content_dirs = os.listdir(os.path.join(self.extract_to, "appunpack", app_name, "common"))
                    for ccdir in common_content_dirs:
                        shutil.copytree(os.path.join(self.extract_to, "appunpack", app_name, "common", ccdir), os.path.join(self.copy_dir, self.partition, ccdir), dirs_exist_ok=True)
