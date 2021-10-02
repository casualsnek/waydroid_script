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

def stop_waydroid():
    print("==> Stopping waydroid and unmounting already mounted images...")
    os.system("waydroid container stop &> /dev/null")
    os.system("umount /var/lib/waydroid/rootfs/vendor/waydroid.prop &> /dev/null")
    os.system("umount /var/lib/waydroid/rootfs/vendor &> /dev/null")
    os.system("umount /var/lib/waydroid/rootfs &> /dev/null")


def get_image_dir():
    # Read waydroid config to get image location
    cfg = configparser.ConfigParser()
    cfg_file = os.environ.get("WAYDROID_CONFIG", "/var/lib/waydroid/waydroid.cfg")
    if not os.path.isfile(cfg_file):
        print("==> Cannot locate waydroid config file, reinit wayland and try again !")
        sys.exit(1)

    cfg.read(cfg_file)
    if "waydroid" not in cfg:
        print("==> Required entry in config was not found, Cannot continue !s")
        sys.exit(1)
    return cfg["waydroid"]["images_path"]


def resize_img(img_file, size):
    # Resize the system image
    print("==> Resizing system image....")
    try:
        subprocess.check_output(["e2fsck -y -f "+img_file], stderr=subprocess.STDOUT, shell=True)
        subprocess.check_output(["resize2fs '{}' {}".format(img_file, size)], stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        print("==> Failed to resize image '{}' .. !  {}".format(img_file, str(e.output.decode())))
        p = input("==> You can exit and retry with sudo or force continue (May fail installation !), Continue ? [y/N]: ")
        if not p.lower() == "y":
            sys.exit(1)


def install_gapps():

    dl_links = {
            "x86_64": ["https://nchc.dl.sourceforge.net/project/opengapps/x86_64/20210918/open_gapps-x86_64-10.0-pico-20210918.zip", "55db1a79b1d41573d7c2cd5927189779"],
            "x86": ["https://altushost-swe.dl.sourceforge.net/project/opengapps/x86/20210918/open_gapps-x86-10.0-pico-20210918.zip", "f5101b20422684904f1e927fc5c7839b"],
            "aarch64": ["https://altushost-swe.dl.sourceforge.net/project/opengapps/arm64/20210918/open_gapps-arm64-10.0-pico-20210918.zip", "0384dcee9a102995ad544533381139c2"],
            "arm": ["https://altushost-swe.dl.sourceforge.net/project/opengapps/arm/20210918/open_gapps-arm-10.0-pico-20210918.zip", "b6674e2fe7ea345d5c21ddf59039201e"]
        }
    if platform.machine() not in dl_links.keys():
        print("==> Unsupported architecture '{}' .. ".format(platform.machine()))
        sys.exit(1)
    opengapps_dl_link = dl_links[platform.machine()][0]
    dl_fname = "open_gapps.zip"
    act_md5 = dl_links[platform.machine()][1]
    loc_md5 = ""
    sys_image_mount = "/tmp/waydroidimage"
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

    if os.path.isfile("/tmp/"+dl_fname):
        with open("/tmp/"+dl_fname,"rb") as f:
            bytes = f.read()
            loc_md5 = hashlib.md5(bytes).hexdigest()
    print("==> Excepted hash: {}  | File hash: {}".format(act_md5, loc_md5))


    system_img = os.path.join(get_image_dir(), "system.img")
    if not os.path.isfile(system_img):
        print("The system image path '{}' from waydroid config is not valid !".format(system_img))
        sys.exit(1)
    print("==> Found system image: "+system_img)


    # Clear mount point
    print("==> Unmounting .. ")
    try:
        subprocess.check_output(["losetup", "-D"], stderr=subprocess.STDOUT)
        subprocess.check_output(["umount", sys_image_mount], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print("==> Warning: umount failed.. {} ".format(str(e.output.decode())))


    # Resize image to get some free space
    resize_img(system_img, "5G")


    # Mount the system image
    if not os.path.exists(sys_image_mount):
        os.makedirs(sys_image_mount)
    try:
        mount = subprocess.check_output(["mount", "-o", "rw", system_img, sys_image_mount], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print("==> Failed to mount system image... !  {}".format(str(e.output.decode())))
        sys.exit(1)

    # Download the file if hash mismatches or if file does not exist
    while not os.path.isfile("/tmp/"+dl_fname) or loc_md5 != act_md5:
        if os.path.isfile("/tmp/"+dl_fname):
            os.remove("/tmp/"+dl_fname)
        print("==> OpenGapps zip not downloaded or hash mismatches, downloading now .....")
        response = requests.get(opengapps_dl_link, stream=True)
        total_size_in_bytes= int(response.headers.get('content-length', 0))
        block_size = 1024 #1 Kibibyte
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
        with open('/tmp/'+dl_fname, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        with open("/tmp/"+dl_fname,"rb") as f:
            bytes = f.read()
            loc_md5 = hashlib.md5(bytes).hexdigest()
        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            print("==> Something went wrong while downloading")
            sys.exit(1)


    # Extract opengapps
    print("==> Extracting opengapps...")
    with zipfile.ZipFile("/tmp/"+dl_fname) as z:
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
    print("==> Unmounting .. ")
    try:
        subprocess.check_output(["umount", sys_image_mount], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print("==> Warning: umount failed.. {} ".format(str(e.output.decode())))
    print("==> OpenGapps installation complete try reiniting/restarting waydroid")
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
    ndk_zip_url = "https://github.com/newbit1/libndk_translation_Module/archive/c6077f3398172c64f55aad7aab0e55fad9110cf3.zip"
    dl_fname = "libndktranslation.zip"
    extract_to = "/tmp/libndkunpack"
    act_md5 = "5e8e0cbde0e672fdc2b47f20a87472fd"
    loc_md5 = ""
    apply_props = {
        "ro.product.cpu.abilist": "x86_64,x86,armeabi-v7a,armeabi", #arm64-v8a,
        "ro.product.cpu.abilist32": "x86,armeabi-v7a,armeabi",
        "ro.product.cpu.abilist64": "x86_64", #,arm64-v8a",
        "ro.dalvik.vm.native.bridge": "libndk_translation.so",
        "ro.enable.native.bridge.exec": "1",
        "ro.ndk_translation.version": "0.2.2",
        "ro.dalvik.vm.isa.arm": "x86",
        "ro.dalvik.vm.isa.arm64": "x86_64"
        }
    init_rc_component = """
on early-init
    mount binfmt_misc binfmt_misc /proc/sys/fs/binfmt_misc

on property:ro.enable.native.bridge.exec=1
    cat /system/etc/binfmt_misc/arm_exe > /proc/sys/fs/binfmt_misc/register
    cat /system/etc/binfmt_misc/arm_dyn >> /proc/sys/fs/binfmt_misc/register
    cat /system/etc/binfmt_misc/arm64_exe >> /proc/sys/fs/binfmt_misc/register
    cat /system/etc/binfmt_misc/arm64_dyn >> /proc/sys/fs/binfmt_misc/register
    """

    system_img = os.path.join(get_image_dir(), "system.img")
    if os.path.isfile("/tmp/"+dl_fname):
        with open("/tmp/"+dl_fname,"rb") as f:
            bytes = f.read()
            loc_md5 = hashlib.md5(bytes).hexdigest()
    if not os.path.isfile(system_img):
        print("The system image path '{}' from waydroid config is not valid !".format(system_img))
        sys.exit(1)
    print("==> Found system image: "+system_img)


    # Clear mount point
    print("==> Unmounting .. ")
    try:
        subprocess.check_output(["losetup", "-D"], stderr=subprocess.STDOUT)
        subprocess.check_output(["umount", sys_image_mount], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print("==> Warning: umount failed.. {} ".format(str(e.output.decode())))

    system_img = os.path.join(get_image_dir(), "system.img")

    # Resize rootfs
    resize_img(system_img, "6G")


    # Mount the system image
    if not os.path.exists(sys_image_mount):
        os.makedirs(sys_image_mount)
    try:
        mount = subprocess.check_output(["mount", "-o", "rw", system_img, sys_image_mount], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print("==> Failed to mount system image... !  {}".format(str(e.output.decode())))
        sys.exit(1)

    # Download the file if hash mismatches or if file does not exist
    while not os.path.isfile("/tmp/"+dl_fname) or loc_md5 != act_md5:
        if os.path.isfile("/tmp/"+dl_fname):
            os.remove("/tmp/"+dl_fname)
        print("==> NDK Translation zip not downloaded or hash mismatches, downloading now .....")
        response = requests.get(ndk_zip_url, stream=True)
        total_size_in_bytes= int(response.headers.get('content-length', 0))
        block_size = 1024 #1 Kibibyte
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
        with open('/tmp/'+dl_fname, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        with open("/tmp/"+dl_fname,"rb") as f:
            bytes = f.read()
            loc_md5 = hashlib.md5(bytes).hexdigest()
        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            print("==> Something went wrong while downloading")
            sys.exit(1)

    # Extract opengapps
    print("==> Extracting archive...")
    with zipfile.ZipFile("/tmp/"+dl_fname) as z:
            z.extractall(extract_to)

    # Copy library file
    print("==> Copying library files ...")
    shutil.copytree(os.path.join(extract_to, "libndk_translation_Module-c6077f3398172c64f55aad7aab0e55fad9110cf3", "system"), os.path.join(sys_image_mount, "system"), dirs_exist_ok=True)

    # Add entries to build.prop
    print("==> Adding arch in build.prop")
    with open(os.path.join(sys_image_mount, "system", "build.prop"), "r") as propfile:
        propcontent = propfile.read()
        for key in apply_props:
            if key not in propcontent:
                propcontent = propcontent+"\n{key}={value}".format(key=key, value=apply_props[key])
            else:
                p = re.compile(r"^{key}=.*$".format(key=key), re.M)
                propcontent = re.sub(p, "{key}={value}".format(key=key, value=apply_props[key]), propcontent)
    with open(os.path.join(sys_image_mount, "system", "build.prop"), "w") as propfile:
        propfile.write(propcontent)


    # Add entry to init.rc
    print("==> Addig entry to init.rc")
    with open(os.path.join(sys_image_mount, "init.rc"), "r") as initfile:
        initcontent = initfile.read()
        if init_rc_component not in initcontent:
            initcontent=initcontent+init_rc_component
    with open(os.path.join(sys_image_mount, "init.rc"), "w") as initfile:
        initfile.write(initcontent)

    # Apply permissions
    #print("==> Setting permissions")
    #for dirname in ["bin", "etc", "lib", "lib64"]:
    #    os.system()

    # Unmount and exit
    print("==> Unmounting .. ")
    try:
        pass
        #subprocess.check_output(["umount", sys_image_mount], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print("==> Warning: umount failed.. {} ".format(str(e.output.decode())))

    print("==> libndk translation installed ! anbox service to apply changes !")


def main():
    about = """s
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

    args = parser.parse_args()
    if args.install:
        stop_waydroid()
        install_gapps()
    elif args.installndk:
        stop_waydroid()
        install_ndk()
    elif args.getid:
        get_android_id()


if __name__ == "__main__":
    main()
