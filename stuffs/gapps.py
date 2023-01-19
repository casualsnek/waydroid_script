import os
import shutil
from stuffs.general import General
from tools.helper import host, run
from tools.logger import Logger

class Gapps(General):
    partition = "system"
    dl_links = {
            "x86_64": ["https://master.dl.sourceforge.net/project/opengapps/x86_64/20220121/open_gapps-x86_64-10.0-pico-20220121.zip?viasf=1", "e8c9a7412f5712eea7948957a62a7d66"],
            "x86": ["https://udomain.dl.sourceforge.net/project/opengapps/x86/20220122/open_gapps-x86-10.0-pico-20220122.zip", "9e39e45584b7ade4529e6be654af7b81"],
            "arm64-v8a": ["https://liquidtelecom.dl.sourceforge.net/project/opengapps/arm64/20220122/open_gapps-arm64-10.0-pico-20220122.zip", "8dfa6e76aeb2d1d5aed40b058e8a852c"],
            "armeabi-v7a": ["https://nav.dl.sourceforge.net/project/opengapps/arm/20220122/open_gapps-arm-10.0-pico-20220122.zip", "a48ccbd25eb0a3c5e30f5db5435f5536"]
        }
    arch = host()
    dl_link = dl_links[arch[0]][0]
    dl_file_name = "open_gapps.zip"
    act_md5 = dl_links[arch[0]][1]
    extract_to = "/tmp/ogapps/extract"
    non_apks = [
        "defaultetc-common.tar.lz",
        "defaultframework-common.tar.lz",
        "googlepixelconfig-common.tar.lz"
        ]
    skip = [
        "setupwizarddefault-x86_64.tar.lz",
        "setupwizardtablet-x86_64.tar.lz"
        ]

    def download(self):
        Logger.info("Downloading OpenGapps now to {} .....".format(self.download_loc))
        super().download()

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