import configparser
import sys
import os
import hashlib
import shutil
import zipfile
import subprocess
import argparse
import platform
from tqdm import tqdm
import requests
import re

download_loc = ""
if os.environ.get("XDG_CACHE_HOME", None) is None:
    download_loc = os.path.join('/', "home", os.environ.get("SUDO_USER", os.environ["USER"]), ".cache", "waydroid_script", "downloads")
else:
    download_loc = os.path.join(os.environ["XDG_CACHE_HOME"], "waydroid_script", "downloads")
    
print(download_loc)

if not os.path.exists(download_loc):
    os.makedirs(download_loc)

def stop_waydroid():
    print("==> Stopping waydroid and unmounting already mounted images...")
    os.system("waydroid container stop &> /dev/null")
    os.system("umount /var/lib/waydroid/rootfs/vendor/waydroid.prop &> /dev/null")
    os.system("umount /var/lib/waydroid/rootfs/vendor &> /dev/null")
    os.system("umount /var/lib/waydroid/rootfs &> /dev/null")

def download_file(url, f_name):
    md5 = ""
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    with open(f_name, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    with open(f_name, "rb") as f:
        bytes = f.read()
        md5 = hashlib.md5(bytes).hexdigest()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("==> Something went wrong while downloading")
        sys.exit(1)
    return md5

def get_image_dir():
    # Read waydroid config to get image location
    cfg = configparser.ConfigParser()
    cfg_file = os.environ.get("WAYDROID_CONFIG", "/var/lib/waydroid/waydroid.cfg")
    if not os.path.isfile(cfg_file):
        print("==> Cannot locate waydroid config file, reinit wayland and try again !")
        sys.exit(1)

    cfg.read(cfg_file)
    if "waydroid" not in cfg:
        print("==> Required entry in config was not found, Cannot continue !s") #magisk
        sys.exit(1)
    return cfg["waydroid"]["images_path"]

def install_gapps():

    dl_links = {
            "x86_64": ["https://master.dl.sourceforge.net/project/opengapps/x86_64/20220121/open_gapps-x86_64-10.0-pico-20220121.zip?viasf=1", "e8c9a7412f5712eea7948957a62a7d66"],
            "x86": ["https://udomain.dl.sourceforge.net/project/opengapps/x86/20220122/open_gapps-x86-10.0-pico-20220122.zip", "9e39e45584b7ade4529e6be654af7b81"],
            "aarch64": ["https://liquidtelecom.dl.sourceforge.net/project/opengapps/arm64/20220122/open_gapps-arm64-10.0-pico-20220122.zip", "8dfa6e76aeb2d1d5aed40b058e8a852c"],
            "arm": ["https://nav.dl.sourceforge.net/project/opengapps/arm/20220122/open_gapps-arm-10.0-pico-20220122.zip", "a48ccbd25eb0a3c5e30f5db5435f5536"]
        }
    if platform.machine() not in dl_links.keys():
        print("==> Unsupported architecture '{}' .. ".format(platform.machine()))
        sys.exit(1)
    google_apps_dl_link = dl_links[platform.machine()][0]
    dl_file_name = os.path.join(download_loc, "open_gapps.zip")
    act_md5 = dl_links[platform.machine()][1]
    loc_md5 = ""
    sys_image_mount = "/var/lib/waydroid/overlay"
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

    if not os.path.exists(extract_to):
        os.makedirs(extract_to)
    if not os.path.exists(os.path.join(extract_to, "appunpack")):
        os.makedirs(os.path.join(extract_to, "appunpack"))

    if os.path.isfile(dl_file_name):
        with open(dl_file_name,"rb") as f:
            bytes = f.read()
            loc_md5 = hashlib.md5(bytes).hexdigest()
    print("==> Excepted hash: {}  | File hash: {}".format(act_md5, loc_md5))

    # Download the file if hash mismatches or if file does not exist
    while not os.path.isfile(dl_file_name) or loc_md5 != act_md5:
        if os.path.isfile(dl_file_name):
            os.remove(dl_file_name)
        print("==> OpenGapps zip not downloaded or hash mismatches, downloading now .....")
        loc_md5 = download_file(google_apps_dl_link, dl_file_name)

    # Extract opengapps
    print("==> Extracting opengapps...")
    with zipfile.ZipFile(dl_file_name) as z:
            z.extractall(extract_to)

    # Now copy the files
    for lz_file in os.listdir(os.path.join(extract_to, "Core")):
        for d in os.listdir(os.path.join(extract_to, "appunpack")):
            shutil.rmtree(os.path.join(extract_to, "appunpack", d))
        if lz_file not in skip:
            if lz_file not in non_apks:
                print("==> Processing app package : "+os.path.join(extract_to, "Core", lz_file))
                os.system("tar --lzip -xvf '{}' -C '{}'>/dev/null".format(os.path.join(extract_to, "Core", lz_file), os.path.join(extract_to, "appunpack")))
                app_name = os.listdir(os.path.join(extract_to, "appunpack"))[0]
                xx_dpi = os.listdir(os.path.join(extract_to, "appunpack", app_name))[0]
                app_priv = os.listdir(os.path.join(extract_to, "appunpack", app_name, "nodpi"))[0]
                app_src_dir = os.path.join(extract_to, "appunpack", app_name, xx_dpi, app_priv)
                for app in os.listdir(app_src_dir):
                    shutil.copytree(os.path.join(app_src_dir, app), os.path.join(sys_image_mount, "system", "priv-app", app), dirs_exist_ok=True)
            else:
                print("==> Processing extra package : "+os.path.join(extract_to, "Core", lz_file))
                os.system("tar --lzip -xvf '{}' -C '{}'>/dev/null".format(os.path.join(extract_to, "Core", lz_file), os.path.join(extract_to, "appunpack")))
                app_name = os.listdir(os.path.join(extract_to, "appunpack"))[0]
                common_content_dirs = os.listdir(os.path.join(extract_to, "appunpack", app_name, "common"))
                for ccdir in common_content_dirs:
                    shutil.copytree(os.path.join(extract_to, "appunpack", app_name, "common", ccdir), os.path.join(sys_image_mount, "system", ccdir), dirs_exist_ok=True)
    print("==> OpenGapps installation complete try re init /restarting waydroid")
    print("==> Please note, google apps wont be usable without device registration !, Use --get-android-id for registration instructions")


def get_android_id():
    try:
        if not os.path.isfile("/var/lib/waydroid/data/data/com.google.android.gsf/databases/gservices.db"):
            print("Cannot access gservices.db, make sure gapps is installed and waydroid was started at least once after installation and make sure waydroid is running !")
            sys.exit(1)
        sqs = """
                SELECT * FROM main WHERE name='android_id'
            """
        queryout = subprocess.check_output(["sqlite3", "/var/lib/waydroid/data/data/com.google.android.gsf/databases/gservices.db", sqs.strip()], stderr=subprocess.STDOUT)
        print(queryout.decode().replace("android_id|", "").strip())
        print("   ^----- Open https://google.com/android/uncertified/?pli=1")
        print("          Login with your google id then submit the form with id shown above")
    except subprocess.CalledProcessError as e:
        print("==> Error getting id... '{}' ".format(str(e.output.decode())))

def install_ndk():
    sys_image_mount = "/tmp/waydroidimage"
    ndk_zip_url = "https://www.dropbox.com/s/eaf4dj3novwiccp/libndk_translation_Module-c6077f3398172c64f55aad7aab0e55fad9110cf3.zip?dl=1"
    dl_file_name = os.path.join(download_loc, "libndktranslation.zip")
    extract_to = "/tmp/libndkunpack" #All catalog files will be marked as executable!
    act_md5 = "4456fc1002dc78e544e8d9721bb24398"
    loc_md5 = ""
    apply_props = {
        "ro.product.cpu.abilist": "x86_64,x86,armeabi-v7a,armeabi,arm64-v8a",
        "ro.product.cpu.abilist32": "x86,armeabi-v7a,armeabi",
        "ro.product.cpu.abilist64": "x86_64,arm64-v8a",
        "ro.dalvik.vm.native.bridge": "libndk_translation.so",
        "ro.enable.native.bridge.exec": "1",
      #  "ro.ndk_translation.version": "0.2.2",
        "ro.dalvik.vm.isa.arm": "x86",
        "ro.dalvik.vm.isa.arm64": "x86_64"
        }
    init_rc_component = """
on early-init
    mount -t binfmt_misc binfmt_misc /proc/sys/fs/binfmt_misc

on property:ro.enable.native.bridge.exec=1
    exec -- /system/bin/sh -c "cat /system/etc/binfmt_misc/arm_exe > /proc/sys/fs/binfmt_misc/register"
    exec -- /system/bin/sh -c "cat /system/etc/binfmt_misc/arm_dyn >> /proc/sys/fs/binfmt_misc/register"
    exec -- /system/bin/sh -c "cat /system/etc/binfmt_misc/arm64_exe >> /proc/sys/fs/binfmt_misc/register"
    exec -- /system/bin/sh -c "cat /system/etc/binfmt_misc/arm64_dyn >> /proc/sys/fs/binfmt_misc/register"
    """
    if os.path.isfile(dl_file_name):
        with open(dl_file_name,"rb") as f:
            bytes = f.read()
            loc_md5 = hashlib.md5(bytes).hexdigest()

    system_img = os.path.join(get_image_dir(), "system.img")
    if not os.path.isfile(system_img):
        print("The system image path '{}' from waydroid config is not valid !".format(system_img))
        sys.exit(1)
    print("==> Found system image: "+system_img)

    # Resize rootfs
    img_size = int(os.path.getsize(system_img)/(1024*1024))

    # Resize image to get some free space
    resize_img(system_img, "{}M".format(img_size+50))

    # Mount the system image
    mount_image(system_img, sys_image_mount)

    # Download the file if hash mismatches or if file does not exist
    while not os.path.isfile(dl_file_name) or loc_md5 != act_md5:
        if os.path.isfile(dl_file_name):
            os.remove(dl_file_name)
        print("==> NDK Translation zip not downloaded or hash mismatches, downloading now .....")
        loc_md5 = download_file(ndk_zip_url, dl_file_name)

    # Extract ndk files
    print("==> Extracting archive...")
    with zipfile.ZipFile(dl_file_name) as z:
            z.extractall(extract_to)

    #Mark ndk files as executable
    print("==> Chmodding...")
    try: os.system("chmod +x "+extract_to+" -R")
    except: print("==> Couldn't mark files as executable!")
    
    # Copy library file
    print("==> Copying library files ...")
    shutil.copytree(os.path.join(extract_to, "libndk_translation_Module-c6077f3398172c64f55aad7aab0e55fad9110cf3", "system"), os.path.join(sys_image_mount, "system"), dirs_exist_ok=True)

    # Add entries to build.prop
    print("==> Adding arch in build.prop")
    with open(os.path.join(sys_image_mount, "system", "build.prop"), "r") as propfile:
        prop_content = propfile.read()
        for key in apply_props:
            if key not in prop_content:
                prop_content = prop_content+"\n{key}={value}".format(key=key, value=apply_props[key])
            else:
                p = re.compile(r"^{key}=.*$".format(key=key), re.M)
                prop_content = re.sub(p, "{key}={value}".format(key=key, value=apply_props[key]), prop_content)
    with open(os.path.join(sys_image_mount, "system", "build.prop"), "w") as propfile:
        propfile.write(prop_content)


    # Add entry to init.rc
    print("==> Adding entry to init.rc")
    # Check if init.rc is located in Android 11's path
    init_path = os.path.join(sys_image_mount, "system", "etc", "init", "hw", "init.rc")
    if not os.path.isfile(init_path):
        # init.rc not found, assuming it's located in the root folder (Android 10 and older)
        init_path = os.path.join(sys_image_mount, "init.rc")
    with open(init_path, "r") as initfile:
        initcontent = initfile.read()
        if init_rc_component not in initcontent:
            initcontent=initcontent+init_rc_component
    with open(init_path, "w") as initfile:
        initfile.write(initcontent)

    # Unmount and exit
    print("==> Unmounting .. ")
    try:
        subprocess.check_output(["umount", sys_image_mount], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print("==> Warning: umount failed.. {} ".format(str(e.output.decode())))

    print("==> libndk translation installed ! Restart waydroid service to apply changes !")


def install_houdini():
    sys_image_mount = "/var/lib/waydroid/overlay"
    prop_file = "/var/lib/waydroid/waydroid_base.prop"
    houdini_zip_url = "https://www.dropbox.com/s/v7g0fluc7e8tod8/libhoudini.zip?dl=1"
    dl_file_name = os.path.join(download_loc, "libhoudini.zip")
    extract_to = "/tmp/houdiniunpack" #All catalog files will be marked as executable!
    act_md5 = "838097117cec7762e958d7cbc209415e"
    loc_md5 = ""

    apply_props = {
        "ro.product.cpu.abilist": "x86_64,x86,arm64-v8a,armeabi-v7a,armeabi",
        "ro.product.cpu.abilist32": "x86,armeabi-v7a,armeabi",
        "ro.product.cpu.abilist64": "x86_64,arm64-v8a",
        "ro.dalvik.vm.native.bridge": "libhoudini.so",
        "ro.enable.native.bridge.exec": "1",
        "ro.dalvik.vm.isa.arm": "x86",
        "ro.dalvik.vm.isa.arm64": "x86_64"
        }
    init_rc_component = """
on early-init
    mount -t binfmt_misc binfmt_misc /proc/sys/fs/binfmt_misc

on property:ro.enable.native.bridge.exec=1
    exec -- /system/bin/sh -c "echo ':arm_exe:M::\\\\x7f\\\\x45\\\\x4c\\\\x46\\\\x01\\\\x01\\\\x01\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x02\\\\x00\\\\x28::/system/bin/houdini:P' > /proc/sys/fs/binfmt_misc/register"
    exec -- /system/bin/sh -c "echo ':arm_dyn:M::\\\\x7f\\\\x45\\\\x4c\\\\x46\\\\x01\\\\x01\\\\x01\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x03\\\\x00\\\\x28::/system/bin/houdini:P' >> /proc/sys/fs/binfmt_misc/register"
    exec -- /system/bin/sh -c "echo ':arm64_exe:M::\\\\x7f\\\\x45\\\\x4c\\\\x46\\\\x02\\\\x01\\\\x01\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x02\\\\x00\\\\xb7::/system/bin/houdini64:P' >> /proc/sys/fs/binfmt_misc/register"
    exec -- /system/bin/sh -c "echo ':arm64_dyn:M::\\\\x7f\\\\x45\\\\x4c\\\\x46\\\\x02\\\\x01\\\\x01\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x03\\\\x00\\\\xb7::/system/bin/houdini64:P' >> /proc/sys/fs/binfmt_misc/register"
    """

    if os.path.isfile(dl_file_name):
        with open(dl_file_name,"rb") as f:
            bytes = f.read()
            loc_md5 = hashlib.md5(bytes).hexdigest()

    # Download the file if hash mismatches or if file does not exist
    while not os.path.isfile(dl_file_name) or loc_md5 != act_md5:
        if os.path.isfile(dl_file_name):
            os.remove(dl_file_name)
        print("==> libhoudini zip not downloaded or hash mismatches, downloading now .....")
        loc_md5 = download_file(houdini_zip_url, dl_file_name)

    # Extract ndk files
    print("==> Extracting archive...")
    with zipfile.ZipFile(dl_file_name) as z:
            z.extractall(extract_to)

    # Mark libhoudini files as executable
    print("==> Chmodding...")
    try: os.system("chmod +x "+extract_to+" -R")
    except: print("==> Couldn't mark files as executable!")

    # Copy library file
    print("==> Copying library files ...")
    shutil.copytree(os.path.join(extract_to, "system"), os.path.join(sys_image_mount, "system"), dirs_exist_ok=True)

    # Add entries to build.prop
    print("==> Adding arch in", prop_file)
    with open(os.path.join(prop_file), "r") as propfile:
        prop_content = propfile.read()
        for key in apply_props:
            if key not in prop_content:
                prop_content = prop_content+"\n{key}={value}".format(key=key, value=apply_props[key])
            else:
                p = re.compile(r"^{key}=.*$".format(key=key), re.M)
                prop_content = re.sub(p, "{key}={value}".format(key=key, value=apply_props[key]), prop_content)
    with open(os.path.join(prop_file), "w") as propfile:
        propfile.write(prop_content)

    # Add entry to init.rc
    print("==> Adding entry to init.rc")
    # Check if init.rc is located in Android 11's path
    init_path = os.path.join(sys_image_mount, "system", "etc", "init", "houdini.rc")
    if not os.path.isfile(init_path):
        os.makedirs(os.path.dirname(init_path), exist_ok=True)
        f = open(init_path, "x")
    with open(init_path, "r") as initfile:
        initcontent = initfile.read()
        if init_rc_component not in initcontent:
            initcontent=initcontent+init_rc_component
    with open(init_path, "w") as initfile:
        initfile.write(initcontent)


    print("==> libhoudini translation installed ! Restart waydroid service to apply changes !")


def install_magisk():
    dl_link = "https://github.com/topjohnwu/Magisk/releases/download/v21.4/Magisk-v21.4.zip"
    busybox_dl_link = "https://github.com/Gnurou/busybox-android/raw/master/busybox-android"
    busybox_dl_file_name = os.path.join(download_loc, "busybox-android")
    dl_file_name = os.path.join(download_loc, "magisk.zip")
    extract_to = "/tmp/magisk_unpack"
    act_md5 = "ee6dd05579776e7de3a6077087846e53"
    busybox_act_md5 = "2e43cc2e8f44b83f9029a6561ce5d8b9"
    sys_image_mount = "/var/lib/waydroid/overlay_rw"
    loc_md5 = ""
    busybox_loc_md5 = ""
    magisk_init = """#!/system/bin/sh
mount -o remount,rw /
rm /sbin/magisk /sbin/magiskpolicy /sbin/magiskinit
cp /magiskinit /sbin/magiskinit
ln -s /sbin/magiskinit /sbin/magisk
ln -s /sbin/magiskinit /sbin/magiskpolicy
mkdir -p /data/adb/magisk
cp /busybox /data/adb/magisk/busybox
cp /util_functions.sh /data/adb/magisk/util_functions.sh
cp /boot_patch.sh /data/adb/magisk/boot_patch.sh
cp /addon.d.sh /data/adb/magisk/addon.d.sh
magisk -c >&2
ln -sf /data /sbin/.magisk/mirror/data
ln -sf /vendor /sbin/.magisk/mirror/vendor
magisk --post-fs-data
sleep 1
magisk --service
magisk --boot-complete
mount -o remount,ro /
    """
    init_rc_component = """on property:dev.bootcomplete=1
    start magisk

service magisk /system/bin/init-magisk.sh
    class main
    user root
    group root
    oneshot
    """
    if os.path.isfile(dl_file_name):
        with open(dl_file_name,"rb") as f:
            bytes = f.read()
            loc_md5 = hashlib.md5(bytes).hexdigest()

    if os.path.isfile(busybox_dl_file_name):
        with open(busybox_dl_file_name,"rb") as f:
            bytes = f.read()
            busybox_loc_md5 = hashlib.md5(bytes).hexdigest()

    # Download magisk
    while not os.path.isfile(dl_file_name) or loc_md5 != act_md5:
        if os.path.isfile(dl_file_name):
            os.remove(dl_file_name)
        print("==> Magisk zip not downloaded or hash mismatches, downloading now .....")
        loc_md5 = download_file(dl_link, dl_file_name)

    # Download busybox android binary
    while not os.path.isfile(busybox_dl_file_name) or busybox_loc_md5 != busybox_act_md5:
        if os.path.isfile(busybox_dl_file_name):
            os.remove(busybox_dl_file_name)
        print("==> BusyBox binary not downloaded or hash mismatches, downloading now .....")
        busybox_loc_md5 = download_file(busybox_dl_link, busybox_dl_file_name)

    # Extract magisk files
    print("==> Extracting archive...")
    with zipfile.ZipFile(dl_file_name) as z:
        z.extractall(extract_to)

    # Now setup and install magisk binary and app
    print("==> Installing magisk now ...")
    if not os.path.isdir(os.path.join(sys_image_mount, "system", "bin")):
        os.makedirs(os.path.join(sys_image_mount, "system", "bin"), exist_ok=True)
    with open(os.path.join(sys_image_mount, "system", "bin", "init-magisk.sh"), "w") as imf:
        imf.write(magisk_init)
    os.system("chmod 755 {}".format(os.path.join(sys_image_mount, "system", "bin", "init-magisk.sh")))
    arch_dir = "x86" if "x86" in platform.machine() else "arm"
    arch = "64" if "64" in platform.machine() else ""
    #prep folders
    if not os.path.isdir(os.path.join(sys_image_mount, "sbin")):
        os.makedirs(os.path.join(sys_image_mount, "sbin"), exist_ok=True)
    shutil.copyfile(os.path.join(extract_to, arch_dir, "magiskinit{arch}".format(arch=arch)),
                    os.path.join(sys_image_mount, "sbin", "magiskinit"))
    shutil.copyfile(os.path.join(extract_to, arch_dir, "magiskinit{arch}".format(arch=arch)),
                    os.path.join(sys_image_mount, "magiskinit"))
    os.system("chmod 755 {} & chmod 755 {}".format(os.path.join(sys_image_mount, "sbin", "magiskinit"), os.path.join(sys_image_mount, "magiskinit")))

    # Copy busybox
    print("==> Installing BusyBox")
    shutil.copyfile(busybox_dl_file_name, os.path.join(sys_image_mount, "busybox"))
    os.system("chmod 755 {}".format(os.path.join(sys_image_mount, "busybox")))

    # Copy files from common directory
    for file in ["util_functions.sh", "boot_patch.sh", "addon.d.sh"]:
        shutil.copyfile(os.path.join(extract_to, "common", file),
                        os.path.join(sys_image_mount, file))
        os.system("chmod 755 {}".format(os.path.join(sys_image_mount, file)))

    # Create symlinks
    print("==> Creating symlinks")
    os.system("cd {root}/sbin && ln -sf magiskinit magiskinit >> /dev/null 2>&1".format(root=sys_image_mount))
    os.system("cd {root}/sbin && ln -sf magiskinit magisk >> /dev/null 2>&1".format(root=sys_image_mount))
    print("==>     magiskinit  ->  magisk")
    os.system("cd {root}/sbin && ln -sf /magiskinit magiskpolicy >> /dev/null 2>&1".format(root=sys_image_mount))
    print("==>     magiskinit  ->  magiskpolicy")

    # Add entry to init.rc
    print("==> Adding entry to magsik.rc")
    init_path = os.path.join(sys_image_mount, "system", "etc", "init", "magisk.rc")
    if not os.path.isfile(init_path):
        os.makedirs(os.path.dirname(init_path), exist_ok=True)
        f = open(init_path, "x")
    with open(init_path, "r") as initfile:
        initcontent = initfile.read()
        if init_rc_component not in initcontent:
            initcontent=initcontent+init_rc_component
    with open(init_path, "w") as initfile:
        initfile.write(initcontent)

    # Install Magisk apk
    if not os.path.exists(os.path.join(sys_image_mount, "system", "priv-app", "Magisk")):
        os.makedirs(os.path.join(sys_image_mount, "system", "priv-app", "Magisk"))
    shutil.copyfile(os.path.join(extract_to, "common", "magisk.apk"),
                    os.path.join(sys_image_mount, "system", "priv-app", "Magisk", "magisk.apk"))


    print("==> Magisk was  installed ! Restart waydroid service to apply changes !")
def main():
    about = """
    WayDroid Helper script v0.3
    Does stuff like installing Gapps, Installing NDK Translation and getting Android ID for device registration.
    Use -h  flag for help !
    """
    parser = argparse.ArgumentParser(description=about, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-g', '--install-gapps',
                        dest='install',
                        help='Install OpenGapps to waydroid',
                        action='store_true')
    parser.add_argument('-n', '--install-ndk-translation',
                        dest='installndk',
                        help='Install experimental libndk translation files',
                        action='store_true')
    parser.add_argument('-i', '--get-android-id', dest='getid',
                        help='Displays your android id for manual registration',
                        action='store_true')
    parser.add_argument('-m', '--install-magisk', dest='magisk',
                        help='Attempts to install Magisk ( Bootless )',
                        action='store_true')
    parser.add_argument('-l', '--install-libhoudini', dest='houdini',
                        help='Install libhoudini for arm translation',
                        action='store_true')

    args = parser.parse_args()
    if args.install:
        stop_waydroid()
        install_gapps()
    elif args.installndk:
        stop_waydroid()
        install_ndk()
    elif args.getid:
        get_android_id()
    elif args.magisk:
        install_magisk()
    elif args.houdini:
        install_houdini()

if __name__ == "__main__":
    main()
