import gzip
import os
import shutil
import re
from stuffs.general import General
from tools.helper import download_file, host, run
from tools.logger import Logger
from tools import container

class Magisk(General):
    partition = "system"
    dl_link = "https://huskydg.github.io/magisk-files/app-release.apk"
    dl_file_name = "magisk.apk"
    extract_to = "/tmp/magisk_unpack"
    magisk_dir = os.path.join(partition, "etc", "init", "magisk")
    machine = host()
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
    bootanim_component = """
on post-fs-data
    start logd
    exec u:r:su:s0 root root -- /system/etc/init/magisk/magisk{arch} --auto-selinux --setup-sbin /system/etc/init/magisk
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
    """.format(arch=machine[1])

    def download(self):
        if os.path.isfile(self.download_loc):
            os.remove(self.download_loc)
        Logger.info("Downloading latest Magisk-Delta to {} now ...".format(self.download_loc))
        download_file(self.dl_link, self.download_loc)    

    def copy(self):
        magisk_absolute_dir = os.path.join(self.copy_dir, self.magisk_dir)
        if not os.path.exists(magisk_absolute_dir):
            os.makedirs(magisk_absolute_dir, exist_ok=True)

        if not os.path.exists(os.path.join(self.copy_dir, "sbin")):
            os.makedirs(os.path.join(self.copy_dir, "sbin"), exist_ok=True)

        Logger.info("Copying magisk libs now ...")
        
        lib_dir = os.path.join(self.extract_to, "lib", self.machine[0])
        for parent, dirnames, filenames in os.walk(lib_dir):
            for filename in filenames:
                o_path = os.path.join(lib_dir, filename)  
                filename = re.search('lib(.*)\.so', filename)
                n_path = os.path.join(magisk_absolute_dir, filename.group(1))
                shutil.copyfile(o_path, n_path)
                run(["chmod", "+x", n_path])
        shutil.copyfile(self.download_loc, os.path.join(magisk_absolute_dir,"magisk.apk") )

        # Updating Magisk from Magisk manager will modify bootanim.rc, 
        # So it is necessary to backup the original bootanim.rc.
        bootanim_path = os.path.join(self.copy_dir, self.partition, "etc", "init", "bootanim.rc")
        gz_filename = os.path.join(bootanim_path)+".gz"
        with gzip.open(gz_filename,'wb') as f_gz:
            f_gz.write(self.oringinal_bootanim.encode('utf-8'))
        with open(bootanim_path, "w") as initfile:
            initfile.write(self.oringinal_bootanim+self.bootanim_component)


    # Delete the contents of upperdir
    def extra1(self):
        if container.use_overlayfs():
            sys_overlay_rw = "/var/lib/waydroid/overlay_rw"
            old_bootanim_rc = os.path.join(sys_overlay_rw, "system","system", "etc", "init", "bootanim.rc")
            old_bootanim_rc_gz = os.path.join(sys_overlay_rw, "system","system", "etc", "init", "bootanim.rc.gz")
            old_magisk = os.path.join(sys_overlay_rw, "system","system", "etc", "init", "magisk")

            if os.path.exists(old_bootanim_rc):
                os.remove(old_bootanim_rc)
            if os.path.exists(old_bootanim_rc_gz):
                os.remove(old_bootanim_rc_gz)
            if os.path.exists(old_magisk):
                if os.path.isdir(old_magisk):
                    shutil.rmtree(old_magisk)
                else:
                    os.remove(old_magisk)
