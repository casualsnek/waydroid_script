import gzip
import os
import shutil
import re
from stuff.general import General
from tools.helper import download_file, get_data_dir, host
from tools.logger import Logger
from tools import container

class Magisk(General):
    id = "magisk delta"
    partition = "system"
    dl_link = "https://huskydg.github.io/magisk-files/app-debug.apk"
    dl_file_name = "magisk.apk"
    extract_to = "/tmp/magisk_unpack"
    magisk_dir = os.path.join(partition, "etc", "init", "magisk")
    files = ["etc/init/magisk", "etc/init/bootanim.rc"]
    oringinal_bootanim = """
service bootanim /system/bin/bootanimation
    class core animation
    user graphics
    group graphics audio
    disabled
    oneshot
    ioprio rt 0
    task_profiles MaxPerformance
    
"""
    bootanim_component = f"""
on post-fs-data
    start logd
    exec u:r:su:s0 root root -- /system/etc/init/magisk/magisk{host()[1]} --auto-selinux --setup-sbin /system/etc/init/magisk
    exec u:r:su:s0 root root -- /system/etc/init/magisk/magiskpolicy --live --magisk "allow * magisk_file lnk_file *"
    mkdir /sbin/.magisk 700
    mkdir /sbin/.magisk/mirror 700
    mkdir /sbin/.magisk/block 700
    copy /system/etc/init/magisk/config /sbin/.magisk/config
    rm /dev/.magisk_unblock
    exec u:r:su:s0 root root -- /sbin/magisk --auto-selinux --post-fs-data
    wait /dev/.magisk_unblock 40
    rm /dev/.magisk_unblock

on zygote-start
    exec u:r:su:s0 root root -- /sbin/magisk --auto-selinux --service

on property:sys.boot_completed=1
    mkdir /data/adb/magisk 755
    exec u:r:su:s0 root root -- /sbin/magisk --auto-selinux --boot-complete
    exec -- /system/bin/sh -c "if [ ! -e /data/data/io.github.huskydg.magisk ] ; then pm install /system/etc/init/magisk/magisk.apk ; fi"
   
on property:init.svc.zygote=restarting
    exec u:r:su:s0 root root -- /sbin/magisk --auto-selinux --zygote-restart
   
on property:init.svc.zygote=stopped
    exec u:r:su:s0 root root -- /sbin/magisk --auto-selinux --zygote-restart
    """

    def download(self):
        if os.path.isfile(self.download_loc):
            os.remove(self.download_loc)
        Logger.info("Downloading latest Magisk-Delta to {} now ...".format(self.download_loc))
        download_file(self.dl_link, self.download_loc)

    # require additional setup
    def setup(self):
        Logger.info("Additional setup")
        magisk_absolute_dir = os.path.join(self.copy_dir, self.magisk_dir)
        data_dir = get_data_dir()
        shutil.copytree(magisk_absolute_dir, os.path.join(data_dir, "adb", "magisk"), dirs_exist_ok=True)

    def copy(self):
        magisk_absolute_dir = os.path.join(self.copy_dir, self.magisk_dir)
        if not os.path.exists(magisk_absolute_dir):
            os.makedirs(magisk_absolute_dir, exist_ok=True)

        if not os.path.exists(os.path.join(self.copy_dir, "sbin")):
            os.makedirs(os.path.join(self.copy_dir, "sbin"), exist_ok=True)

        Logger.info("Copying magisk libs now ...")
        
        lib_dir = os.path.join(self.extract_to, "lib", self.arch[0])
        for parent, dirnames, filenames in os.walk(lib_dir):
            for filename in filenames:
                o_path = os.path.join(lib_dir, filename)  
                filename = re.search('lib(.*)\.so', filename)
                n_path = os.path.join(magisk_absolute_dir, filename.group(1))
                shutil.copyfile(o_path, n_path)
        shutil.copyfile(self.download_loc, os.path.join(magisk_absolute_dir,"magisk.apk") )
        shutil.copytree(os.path.join(self.extract_to, "assets", "chromeos"), os.path.join(magisk_absolute_dir, "chromeos"), dirs_exist_ok=True)
        assets_files = [
            "addon.d.sh",
            "boot_patch.sh",
            "stub.apk",
            "util_functions.sh"
        ]
        for f in assets_files:
            shutil.copyfile(os.path.join(self.extract_to, "assets", f), os.path.join(magisk_absolute_dir, f))

        # Updating Magisk from Magisk manager will modify bootanim.rc, 
        # So it is necessary to backup the original bootanim.rc.
        bootanim_path = os.path.join(self.copy_dir, self.partition, "etc", "init", "bootanim.rc")
        gz_filename = os.path.join(bootanim_path)+".gz"
        with gzip.open(gz_filename,'wb') as f_gz:
            f_gz.write(self.oringinal_bootanim.encode('utf-8'))
        with open(bootanim_path, "w") as initfile:
            initfile.write(self.oringinal_bootanim+self.bootanim_component)

    def set_path_perm(self, path):
        if "magisk" in path.split("/"):
            perms = [0, 2000, 0o755, 0o755]
        else:
            perms = [0, 0, 0o755, 0o644]

        mode = os.stat(path).st_mode

        if os.path.isdir(path):
            mode |= perms[2]
        else:
            mode |= perms[3]

        os.chown(path, perms[0], perms[1])
        os.chmod(path, mode)

    def extra1(self):
        self.delete_upper()
        self.setup()
    
    # Delete the contents of upperdir
    def delete_upper(self):
        if container.use_overlayfs():
            sys_overlay_rw = "/var/lib/waydroid/overlay_rw"
            files = [
                "system/system/etc/init/bootanim.rc",
                "system/system/etc/init/bootanim.rc.gz",
                "system/system/etc/init/magisk",               
                "system/system/addon.d/99-magisk.sh",
                "vendor/etc/selinux/precompiled_sepolicy"
            ]

            for f in files:
                file = os.path.join(sys_overlay_rw, f)
                if os.path.isdir(file):
                    shutil.rmtree(file)
                elif os.path.isfile(file) or os.path.exists(file):
                    os.remove(file)
    
    def extra2(self):
        self.delete_upper()
        data_dir = get_data_dir()
        files = [
            os.path.join(data_dir, "adb/magisk.db"),
            os.path.join(data_dir, "adb/magisk")
        ]
        for file in files:
            if os.path.isdir(file):
                shutil.rmtree(file)
            elif os.path.isfile(file):
                os.remove(file)
        bootanim_path = os.path.join(self.copy_dir, self.partition, "etc", "init", "bootanim.rc")
        if container.use_overlayfs():
            if os.path.exists(bootanim_path):
                os.remove(bootanim_path)
        else:
            with open(bootanim_path, "w") as initfile:
                initfile.write(self.oringinal_bootanim)
