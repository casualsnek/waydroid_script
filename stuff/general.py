import configparser
import glob
import os
import shutil
import zipfile
import hashlib
from tools.helper import download_file, get_download_dir, host
from tools import container
from tools.logger import Logger


class General:
    files = []

    @property
    def arch(self):
        return host()

    @property
    def skip_extract(self):
        return False

    @property
    def download_loc(self):
        return os.path.join(get_download_dir(), self.dl_file_name)

    @property
    def copy_dir(self):
        if container.use_overlayfs():
            return "/var/lib/waydroid/overlay"
        else:
            return "/tmp/waydroid"

    def download(self):
        Logger.info("Downloading {} now to {} .....".format(
            self.dl_file_name, self.download_loc))
        loc_md5 = ""
        if os.path.isfile(self.download_loc):
            with open(self.download_loc, "rb") as f:
                bytes = f.read()
                loc_md5 = hashlib.md5(bytes).hexdigest()
        while not os.path.isfile(self.download_loc) or loc_md5 != self.act_md5:
            if os.path.isfile(self.download_loc):
                os.remove(self.download_loc)
                Logger.warning(
                    "md5 mismatches, redownloading now ....")
            loc_md5 = download_file(self.dl_link, self.download_loc)

    def remove(self):
        for f in self.files:
            file = os.path.join(self.copy_dir, self.partition, f)
            if "*" in file:
                for wildcard_file in glob.glob(file):
                    if os.path.isdir(wildcard_file):
                        shutil.rmtree(wildcard_file)
                    elif os.path.isfile(wildcard_file):
                        os.remove(wildcard_file)
            else:
                if os.path.isdir(file):
                    shutil.rmtree(file)
                elif os.path.isfile(file):
                    os.remove(file)

    def extract(self):
        Logger.info(f"Extracting {self.download_loc} to {self.extract_to}")
        with zipfile.ZipFile(self.download_loc) as z:
            z.extractall(self.extract_to)

    def add_props(self):
        bin_dir = os.path.join(self.copy_dir, "system", "etc")
        resetprop_rc = os.path.join(
            self.copy_dir, "system/etc/init/resetprop.rc")
        if not os.path.isfile(os.path.join(bin_dir, "resetprop")):
            if not os.path.exists(bin_dir):
                os.makedirs(bin_dir)
            shutil.copy(os.path.join(os.path.join(os.path.dirname(__file__), "..", "bin",
                        self.arch[0], "resetprop")), bin_dir)
            os.chmod(os.path.join(bin_dir, "resetprop"), 0o755)
        if not os.path.isfile(os.path.join(bin_dir, "resetprop.sh")):
            with open(os.path.join(bin_dir, "resetprop.sh"), "w") as f:
                f.write("#!/system/bin/sh\n")
                f.write(
                    "while read line; do /system/etc/resetprop ${line%=*} ${line#*=}; done < /vendor/waydroid.prop\n")
            os.chmod(os.path.join(bin_dir, "resetprop.sh"), 0o755)
        if not os.path.isfile(resetprop_rc):
            if not os.path.exists(os.path.dirname(resetprop_rc)):
                os.makedirs(os.path.dirname(resetprop_rc))
            with open(resetprop_rc, "w") as f:
                f.write(
                    "on post-fs-data\n    exec u:r:su:s0 root root -- /system/bin/sh /system/bin/resetprop.sh")
            os.chmod(resetprop_rc, 0o644)

        cfg = configparser.ConfigParser()
        cfg.read("/var/lib/waydroid/waydroid.cfg")

        for key in self.apply_props.keys():
            if self.apply_props[key]:
                cfg.set('properties', key, self.apply_props[key])

        with open("/var/lib/waydroid/waydroid.cfg", "w") as f:
            cfg.write(f)

    def extract_app_lib(self, apk_file_path):
        lib_dest_dir = os.path.dirname(apk_file_path)
        with zipfile.ZipFile(apk_file_path, "r") as apk:
            for file_info in apk.infolist():
                file_name = file_info.filename
                file_path = os.path.join(lib_dest_dir, file_name)
                if file_info.filename.startswith(f"lib/{self.arch[0]}/") and file_name.endswith(".so"):
                    os.makedirs(os.path.dirname(
                        file_path), exist_ok=True)
                    with apk.open(file_info.filename) as src_file, open(file_path, "wb") as dest_file:
                        # Logger.info(f"{src_file} -> {dest_file}")
                        shutil.copyfileobj(src_file, dest_file)

    def set_path_perm(self, path):
        if "bin" in path.split("/"):
            perms = [0, 2000, 0o755, 0o777]
        else:
            perms = [0, 0, 0o755, 0o644]

        mode = os.stat(path).st_mode

        if os.path.isdir(path):
            mode |= perms[2]
        else:
            mode |= perms[3]

        os.chown(path, perms[0], perms[1])
        os.chmod(path, mode)

    def set_perm2(self, path, recursive=False):
        if not os.path.exists(path):
            return

        if recursive and os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for dir in dirs:
                    self.set_path_perm(os.path.join(root, dir))
                for file in files:
                    self.set_path_perm(os.path.join(root, file))
        else:
            self.set_path_perm(path)

    def set_perm(self):
        for f in self.files:
            path = os.path.join(self.copy_dir, self.partition, f)
            if "*" in path:
                for wildcard_file in glob.glob(path):
                    self.set_perm2(wildcard_file, recursive=True)
            else:
                self.set_perm2(path, recursive=True)

    def remove_props(self):
        cfg = configparser.ConfigParser()
        cfg.read("/var/lib/waydroid/waydroid.cfg")

        for key in self.apply_props.keys():
            cfg.remove_option('properties', key)

        with open("/var/lib/waydroid/waydroid.cfg", "w") as f:
            cfg.write(f)

    def copy(self):
        pass

    def extra1(self):
        pass

    def extra2(self):
        pass

    def install(self):
        self.download()
        if not self.skip_extract:
            self.extract()
        self.copy()
        self.extra1()
        if hasattr(self, "apply_props"):
            self.add_props()
        self.set_perm()
        Logger.info(f"{self.id} installation finished")

    def uninstall(self):
        self.remove()
        if hasattr(self, "apply_props"):
            self.remove_props()
        self.extra2()
        self.set_perm()
        Logger.info("Uninstallation finished")
