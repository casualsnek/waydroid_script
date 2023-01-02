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
import gzip

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
   # sys_image_mount = "/tmp/waydroidimage"
    sys_image_mount = "/var/lib/waydroid/overlay"
    prop_file = "/var/lib/waydroid/waydroid_base.prop"
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

    #system_img = os.path.join(get_image_dir(), "system.img")
    #if not os.path.isfile(system_img):
    #    print("The system image path '{}' from waydroid config is not valid !".format(system_img))
    #    sys.exit(1)
    #print("==> Found system image: "+system_img)

    # Resize rootfs
    #img_size = int(os.path.getsize(system_img)/(1024*1024))

    # Resize image to get some free space
    #resize_img(system_img, "{}M".format(img_size+50))

    # Mount the system image
    #mount_image(system_img, sys_image_mount)

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

    ##add this
    # Add entries to build.prop
    #print("==> Adding arch in build.prop")
    #with open(os.path.join(sys_image_mount, "system", "build.prop"), "r") as propfile:
    #    prop_content = propfile.read()
    #    for key in apply_props:
    #        if key not in prop_content:
    #            prop_content = prop_content+"\n{key}={value}".format(key=key, value=apply_props[key])
    #        else:
    #            p = re.compile(r"^{key}=.*$".format(key=key), re.M)
    #            prop_content = re.sub(p, "{key}={value}".format(key=key, value=apply_props[key]), prop_content)
    #with open(os.path.join(sys_image_mount, "system", "build.prop"), "w") as propfile:
    #    propfile.write(prop_content)

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

    ###add This
    ## Add entry to init.rc
    #print("==> Adding entry to init.rc")
    ## Check if init.rc is located in Android 11's path
    #init_path = os.path.join(sys_image_mount, "system", "etc", "init", "hw", "init.rc")
    #if not os.path.isfile(init_path):
    #    # init.rc not found, assuming it's located in the root folder (Android 10 and older)
    #    init_path = os.path.join(sys_image_mount, "init.rc")
    #with open(init_path, "r") as initfile:
    #    initcontent = initfile.read()
    #    if init_rc_component not in initcontent:
    #        initcontent=initcontent+init_rc_component
    #with open(init_path, "w") as initfile:
    #    initfile.write(initcontent)

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

    # Unmount and exit
    ##print("==> Unmounting .. ")
    ##try:
    ##    subprocess.check_output(["umount", sys_image_mount], stderr=subprocess.STDOUT)
    ##except subprocess.CalledProcessError as e:
    ##    print("==> Warning: umount failed.. {} ".format(str(e.output.decode())))

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
    dl_link = "https://huskydg.github.io/magisk-files/app-release.apk"
    dl_file_name = os.path.join(download_loc, "magisk.apk")
    extract_to = "/tmp/magisk_unpack"
    # sys_overlay_dir = "/var/lib/waydroid/overlay_rw/system"
    sys_overlay_dir = "/var/lib/waydroid/overlay"
    merge_dir = "/var/lib/waydroid/rootfs"
    magisk_dir = os.path.join(sys_overlay_dir, "system", "etc", "init", "magisk")
    sys_overlay_rw = "/var/lib/waydroid/overlay_rw"
    arch_dir = "x86" if "x86" in platform.machine() else "arm"
    arch = "_64" if "64" in platform.machine() else ""
    init_rc_component = """
on post-fs-data
    start logd
    exec - root root -- /system/etc/init/magisk/magisk{arch} --setup-sbin /system/etc/init/magisk
    exec - root root -- /system/etc/init/magisk/magiskpolicy --live --magisk "allow * magisk_file lnk_file *"
    mkdir /sbin/.magisk 700
    mkdir /sbin/.magisk/mirror 700
    mkdir /sbin/.magisk/block 700
    copy /system/etc/init/magisk/config /sbin/.magisk/config
    rm /dev/.magisk_unblock
    start FAhW7H9G5sf
    wait /dev/.magisk_unblock 40
    rm /dev/.magisk_unblock
service FAhW7H9G5sf /sbin/magisk --post-fs-data
    user root
    seclabel -
    oneshot
service HLiFsR1HtIXVN6 /sbin/magisk --service
    class late_start
    user root
    seclabel -
    oneshot
on property:sys.boot_completed=1
    mkdir /data/adb/magisk 755
    exec - root root -- /sbin/magisk --boot-complete
    exec -- /system/bin/sh -c "if [ ! -e /data/data/io.github.huskydg.magisk ] ; then pm install /system/etc/init/magisk/magisk.apk; fi"
   
on property:init.svc.zygote=restarting
    exec - root root -- /sbin/magisk --zygote-restart
   
on property:init.svc.zygote=stopped
    exec - root root -- /sbin/magisk --zygote-restart
    """.format(arch=32 if arch=="" else 64)

    if "RUNNING" not in subprocess.check_output ("waydroid status | grep Container | awk -F'[:\t]' '{print $3}'", shell=True).decode():
        print("Please make sure waydroid container is running!")
        sys.exit(1)

    # Clear overlay_rw
    print("==> Deleting residual files...")
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

    # Download magisk
    if os.path.isfile(dl_file_name):
        os.remove(dl_file_name)
    print("==> Downloading latest Magisk-Delta now .....")
    download_file(dl_link, dl_file_name)

    # Extract magisk files
    print("==> Extracting archive...")
    with zipfile.ZipFile(dl_file_name) as z:
        z.extractall(extract_to)

    if not os.path.exists(magisk_dir):
        os.makedirs(magisk_dir, exist_ok=True)

    if not os.path.exists(os.path.join(sys_overlay_dir, "sbin")):
        os.makedirs(os.path.join(sys_overlay_dir, "sbin"), exist_ok=True)
    
    # Now setup and install magisk binary and app
    print("==> Installing magisk now ...")
    
    lib_dir = os.path.join(extract_to, "lib", "{arch_dir}{arch}".format(arch_dir=arch_dir, arch=arch))
    for parent, dirnames, filenames in os.walk(lib_dir):
        for filename in filenames:
            o_path = os.path.join(lib_dir, filename)  
            filename = re.search('lib(.*)\.so', filename)
            n_path = os.path.join(magisk_dir, filename.group(1))
            shutil.copyfile(o_path, n_path)
    shutil.copyfile(dl_file_name, os.path.join(magisk_dir,"magisk.apk") )

    # Mark magisk files as executable
    print("==> Chmodding...")
    try: os.system("chmod +x "+ os.path.join(magisk_dir, "magisk*"))
    except: print("==> Couldn't mark files as executable!")

    # Updating Magisk from Magisk manager will modify bootanim.rc, 
    # So it is necessary to backup the original bootanim.rc.
    print("==> Adding entry to bootanim.rc")

    bootanim = os.path.join(sys_overlay_dir, "system", "etc", "init", "bootanim.rc")
    original_bootanim = os.path.join(merge_dir, "system", "etc", "init", "bootanim.rc")

    if not os.path.isfile(bootanim):
        os.makedirs(os.path.dirname(bootanim), exist_ok=True)  
    gz_filename = bootanim+".gz"
    with open(original_bootanim,'rb') as f_ungz:
        with gzip.open(gz_filename,'wb') as f_gz:
            f_gz.writelines(f_ungz)
    with open(original_bootanim, "r") as initfile:
        initcontent = initfile.read()
        if init_rc_component not in initcontent:
            initcontent=initcontent+init_rc_component
    with open(bootanim, "w") as initfile:
        initfile.write(initcontent)

    print("==> Magisk was  installed ! Restart waydroid service to apply changes !")
     
def install_widevine():
    vendor_image_mount = "/var/lib/waydroid/overlay/vendor"
    widevine_zip_url = "https://codeload.github.com/supremegamers/vendor_google_proprietary_widevine-prebuilt/zip/refs/heads/chromeos_hatch"
    dl_file_name = os.path.join(download_loc, "widevine.zip")
    extract_to = "/tmp/widevineunpack" #All catalog files will be marked as executable!
    act_md5 = "7fe3b2a9502da9ad63189a077c457ad2"
    loc_md5 = ""

    if os.path.isfile(dl_file_name):
        with open(dl_file_name,"rb") as f:
            bytes = f.read()
            loc_md5 = hashlib.md5(bytes).hexdigest()

    # Download the file if hash mismatches or if file does not exist
    while not os.path.isfile(dl_file_name) or loc_md5 != act_md5:
        if os.path.isfile(dl_file_name):
            os.remove(dl_file_name)
        print("==> windevine zip not downloaded or hash mismatches, downloading now .....")
        loc_md5 = download_file(widevine_zip_url, dl_file_name)

    # Extract widevine files
    print("==> Extracting archive...")
    with zipfile.ZipFile(dl_file_name) as z:
            z.extractall(extract_to)
    
    #Mark widevine files as executable
    print("==> Chmodding...")
    try: os.system("chmod +x "+extract_to+" -R")
    except: print("==> Couldn't mark files as executable!")

    # Copy library file
    print("==> Copying library files ...")
    shutil.copytree(os.path.join(extract_to, "vendor_google_proprietary_widevine-prebuilt-chromeos_hatch", "prebuilts"), vendor_image_mount, dirs_exist_ok=True)
    
    print("==> Widevine installed ! Restart waydroid service to apply changes !")
    
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
    parser.add_argument('-w', '--install-windevine', dest='widevine',
                        help='Integrate Widevine DRM (L3)',
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
    elif args.widevine:
        install_widevine()

if __name__ == "__main__":
    main()
