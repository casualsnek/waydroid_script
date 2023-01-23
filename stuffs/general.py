import configparser
import os
import re
import zipfile
import hashlib
from tools import images
from tools.helper import download_file, get_download_dir
from tools import container
from tools.logger import Logger

class General:
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
        Logger.info("Downloading {} now to {} .....".format(self.dl_file_name, self.download_loc))
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

    def extract(self):
        Logger.info("Extracting archive...")
        with zipfile.ZipFile(self.download_loc) as z:
            z.extractall(self.extract_to)

    def add_props(self):
        cfg = configparser.ConfigParser()
        cfg.read("/var/lib/waydroid/waydroid.cfg")

        for key in self.apply_props.keys():
            cfg.set('properties', key, self.apply_props[key])
        
        with open("/var/lib/waydroid/waydroid.cfg", "w") as f:
            cfg.write(f)

    def mount(self):
        img = os.path.join(images.get_image_dir(), self.partition+".img")
        mount_point = ""
        if self.partition == "system":
            mount_point = os.path.join(self.copy_dir)
        else:
            mount_point = os.path.join(self.copy_dir, self.partition)
        Logger.info("Mounting {} to {}".format(img, mount_point))
        images.mount(img, mount_point)

    def resize(self):
        img = os.path.join(images.get_image_dir(), self.partition+".img")
        img_size = int(os.path.getsize(img)/(1024*1024))
        new_size = "{}M".format(img_size+500)
        Logger.info("Resizing {} to {}".format(img, new_size))
        images.resize(img, new_size)

    def umount(self):
        mount_point = ""
        if self.partition == "system":
            mount_point = os.path.join(self.copy_dir)
        else:
            mount_point = os.path.join(self.copy_dir, self.partition)
        Logger.info("Umounting {}".format(mount_point))
        images.umount(mount_point)

    def stop(self):
        if container.use_dbus():
            self.session = container.get_session()
        container.stop()

    def start(self):
        if container.use_dbus() and self.session:
            container.start(self.session)
        else:
            container.start()

    def restart(self):
        self.stop()
        self.start()

    def copy(self):
        pass

    def extra1(self):
        pass

    def extra2(self):
        pass

    def install(self):
        if container.use_overlayfs():
            self.download()
            if not self.skip_extract:
                self.extract()
            self.copy()
            self.extra1()
            if hasattr(self, "apply_props"):
                self.add_props()
            self.restart()
            self.extra2()
        else:
            self.stop()
            self.download()
            if not self.skip_extract:
                self.extract()
            self.resize()
            self.mount()
            self.copy()
            self.extra1()
            if hasattr(self, "apply_props"):
                self.add_props()
            self.umount()
            self.start()
            self.extra2()
        Logger.info("Installation finished")
