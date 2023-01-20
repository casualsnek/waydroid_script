import os
import re
import zipfile
import hashlib
from tools import images
from tools.helper import download_file, get_download_dir, run
from tools.container import DBusContainerService
from tools.logger import Logger

class General:
    @property
    def download_loc(self):
        return os.path.join(get_download_dir(), self.dl_file_name)

    @property
    def copy_dir(self):
        if self.use_overlayfs:
            return "/var/lib/waydroid/overlay"
        else:
            return "/tmp/waydroid"

    @property
    def use_dbus(self):
        try:
            DBusContainerService()
        except:
            return False
        return True

    @property
    def use_overlayfs(self):
        with open("/var/lib/waydroid/waydroid.cfg") as f:
            cont=f.read()
            if re.search("mount_overlays[ \t]*=[ \t]*True", cont):
                return True
            return False

    def download(self):
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
        with open(os.path.join("/var/lib/waydroid/waydroid_base.prop"), "r") as propfile:
            prop_content = propfile.read()
            for key in self.apply_props:
                if key not in prop_content:
                    prop_content = prop_content+"\n{key}={value}".format(key=key, value=self.apply_props[key])
                else:
                    p = re.compile(r"^{key}=.*$".format(key=key), re.M)
                    prop_content = re.sub(p, "{key}={value}".format(key=key, value=self.apply_props[key]), prop_content)
        with open(os.path.join("/var/lib/waydroid/waydroid_base.prop"), "w") as propfile:
            propfile.write(prop_content)        

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
        if self.use_dbus:
            self.session = DBusContainerService().GetSession()
            if self.session:
                DBusContainerService().Stop(False)
        else:
            run(["waydroid", "container", "stop"])

    def start(self):
        if self.use_dbus and self.session:
            DBusContainerService().Start(self.session)
        else:
            run(["systemctl", "restart", "waydroid-container.service"])

    def restart(self):
        self.stop()
        self.start()

    def copy(self):
        pass

    def install(self):
        if self.use_overlayfs:
            self.download()
            self.extract()
            self.copy()
            if hasattr(self, "apply_props"):
                self.add_props()
            self.restart()
        else:
            self.stop()
            self.download()
            self.extract()
            self.resize()
            self.mount()
            self.copy()
            if hasattr(self, "apply_props"):
                self.add_props()
            self.umount()
            self.start()
        Logger.info("Installation finished")
