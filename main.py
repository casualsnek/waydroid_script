#!/usr/bin/env python3
try:
    from InquirerPy import inquirer
    from InquirerPy.base.control import Choice
    from InquirerPy.separator import Separator
    HAS_INQUIRER = True
except Exception:
    HAS_INQUIRER = False
import argparse
import json
import os
import shutil
from typing import List
from stuff.android_id import AndroidId
from stuff.gapps import Gapps
from stuff.general import General
from stuff.hidestatusbar import HideStatusBar
from stuff.houdini import Houdini
from stuff.magisk import Magisk
from stuff.microg import MicroG
from stuff.mitm import Mitm
from stuff.ndk import Ndk
from stuff.nodataperm import Nodataperm
from stuff.smartdock import Smartdock
from stuff.widevine import Widevine
from stuff.fdroidpriv import FDroidPriv
import tools.helper as helper
from tools import container
from tools import images

import argparse

from tools.logger import Logger


STATE_FILE = "/var/lib/waydroid/waydroid_script_state.json"


def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"installed": [], "hacks": []}


def save_state(state):
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        Logger.warning("Could not save state: {}".format(e))


def get_certified(args):
    AndroidId().get_id()


def status_app(args):
    state = load_state()
    print("Waydroid script state")
    print("  Installed extras: {}".format(", ".join(state.get("installed", [])) or "none"))
    print("  Hacks: {}".format(", ".join(state.get("hacks", [])) or "none"))
    print("  XDG_SESSION_TYPE: {}".format(os.environ.get("XDG_SESSION_TYPE", "unknown")))
    try:
        import configparser
        cfg = configparser.ConfigParser()
        cfg.read("/var/lib/waydroid/waydroid.cfg")
        print("  Android images path: {}".format(cfg.get("waydroid", "images_path", fallback="unknown")))
        print("  Overlayfs: {}".format(cfg.get("waydroid", "mount_overlays", fallback="unknown")))
    except Exception:
        pass


def backup_images(args):
    import datetime
    try:
        img_dir = images.get_image_dir()
    except Exception as e:
        Logger.error(str(e))
        return
    backup_dir = os.path.join("/var/cache/waydroid-script", "backups",
                              datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(backup_dir, exist_ok=True)
    for name in ("system.img", "vendor.img"):
        src = os.path.join(img_dir, name)
        if os.path.isfile(src):
            Logger.info("Backing up {} to {}".format(src, backup_dir))
            shutil.copy2(src, os.path.join(backup_dir, name))
    Logger.info("Backup finished: {}".format(backup_dir))


def restore_images(args):
    backup_root = "/var/cache/waydroid-script/backups"
    if not os.path.isdir(backup_root):
        Logger.error("No backups found")
        return
    backups = sorted(os.listdir(backup_root))
    if not backups:
        Logger.error("No backups found")
        return
    latest = os.path.join(backup_root, backups[-1])
    try:
        img_dir = images.get_image_dir()
    except Exception as e:
        Logger.error(str(e))
        return
    for name in ("system.img", "vendor.img"):
        src = os.path.join(latest, name)
        dst = os.path.join(img_dir, name)
        if os.path.isfile(src):
            Logger.info("Restoring {} to {}".format(src, dst))
            shutil.copy2(src, dst)
    Logger.info("Restore finished from {}".format(latest))


def mount(partition, copy_dir):
    img = os.path.join(images.get_image_dir(), partition+".img")
    mount_point = ""
    if partition == "system":
        mount_point = os.path.join(copy_dir)
    else:
        mount_point = os.path.join(copy_dir, partition)
    Logger.info("Mounting {} to {}".format(img, mount_point))
    images.mount(img, mount_point)


def resize(partition):
    img = os.path.join(images.get_image_dir(), partition+".img")
    img_size = int(os.path.getsize(img)/(1024*1024))
    new_size = "{}M".format(img_size+500)
    Logger.info("Resizing {} to {}".format(img, new_size))
    images.resize(img, new_size)


def umount(partition, copy_dir):
    mount_point = ""
    if partition == "system":
        mount_point = os.path.join(copy_dir)
    else:
        mount_point = os.path.join(copy_dir, partition)
    Logger.info("Umounting {}".format(mount_point))
    images.umount(mount_point)


def install_app(args):
    install_list: List[General] = []
    app = args.app
    if "gapps" in app:
        install_list.append(Gapps(args.android_version))
    if "libndk" in app and "houdini" not in app:
        arch = helper.host()[0]
        if arch == "x86_64":
            install_list.append(Ndk(args.android_version))
        else:
            Logger.warn("libndk is not supported on your CPU")
    if "libhoudini" in app and "ndk" not in app:
        arch = helper.host()[0]
        if arch == "x86_64":
            install_list.append(Houdini(args.android_version))
        else:
            Logger.warn("libhoudini is not supported on your CPU")
    if "magisk" in app:
        install_list.append(Magisk())
    if "widevine" in app:
        install_list.append(Widevine(args.android_version))
    if "smartdock" in app:
        install_list.append(Smartdock())
    if "microg" in app:
        install_list.append(MicroG(args.android_version, args.microg_variant))
    if "mitm" in app:
        install_list.append(Mitm(args.ca_cert_file))
    if "fdroidpriv" in app:
        install_list.append(FDroidPriv(args.android_version))

    if not container.use_overlayfs():
        copy_dir = "/tmp/waydroid"
        container.stop()

        resize_system, resize_vendor = False, False
        for item in install_list:
            if item.partition == "system":
                resize_system = True
            elif item.partition == "vendor":
                resize_vendor = True

        if resize_system:
            resize("system")
        if resize_vendor:
            resize("vendor")

        mount("system", copy_dir)
        mount("vendor", copy_dir)

    for item in install_list:
        item.install()

    if not container.use_overlayfs():
        umount("vendor", copy_dir)
        umount("system", copy_dir)

    container.upgrade()

    state = load_state()
    for app in getattr(args, "app", []):
        if app not in state.get("installed", []):
            state.setdefault("installed", []).append(app)
    save_state(state)


def remove_app(args):
    remove_list: List[General] = []
    app = args.app
    if "gapps" in app:
        remove_list.append(Gapps(args.android_version))
    if "libndk" in app and "houdini" not in app:
        remove_list.append(Ndk(args.android_version))
    if "libhoudini" in app and "ndk" not in app:
        remove_list.append(Houdini(args.android_version))
    if "magisk" in app:
        remove_list.append(Magisk())
    if "widevine" in app:
        remove_list.append(Widevine(args.android_version))
    if "smartdock" in app:
        remove_list.append(Smartdock())
    if "microg" in app:
        remove_list.append(MicroG(args.android_version, args.microg_variant))
    if "mitm" in app:
        remove_list.append(Mitm())
    if "fdroidpriv" in app:
        remove_list.append(FDroidPriv(args.android_version))
    if "nodataperm" in app:
        remove_list.append(Nodataperm(args.android_version))
    if "hidestatusbar" in app:
        remove_list.append(HideStatusBar())

    if not container.use_overlayfs():
        copy_dir = "/tmp/waydroid"
        container.stop()
        mount("system", copy_dir)
        mount("vendor", copy_dir)

    for item in remove_list:
        item.uninstall()

    if not container.use_overlayfs():
        umount("vendor", copy_dir)
        umount("system", copy_dir)

    container.upgrade()

    state = load_state()
    for app in getattr(args, "app", []):
        if app in state.get("installed", []):
            state["installed"].remove(app)
        if app in state.get("hacks", []):
            state["hacks"].remove(app)
    save_state(state)


def hack_option(args):
    Logger.warning(
        "If these hacks cause any problems, run `sudo python main.py remove <hack_option>` to remove")

    hack_list: List[General] = []
    options = args.option_name
    if "nodataperm" in options:
        hack_list.append(Nodataperm(args.android_version))
    if "hidestatusbar" in options:
        hack_list.append(HideStatusBar(args.android_version))

    if not container.use_overlayfs():
        copy_dir = "/tmp/waydroid"
        container.stop()

        resize_system, resize_vendor = False, False
        for item in hack_list:
            if item.partition == "system":
                resize_system = True
            elif item.partition == "vendor":
                resize_vendor = True

        if resize_system:
            resize("system")
        if resize_vendor:
            resize("vendor")

        mount("system", copy_dir)
        mount("vendor", copy_dir)

    for item in hack_list:
        item.install()

    if not container.use_overlayfs():
        umount("vendor", copy_dir)
        umount("system", copy_dir)

    container.upgrade()

    state = load_state()
    for opt in getattr(args, "option_name", []):
        if opt not in state.get("hacks", []):
            state.setdefault("hacks", []).append(opt)
    save_state(state)


def interact_fancy():
    os.system("clear")
    args = argparse.Namespace()
    android_version = inquirer.select(
        message="Select Android version",
        instruction="(\u2191\u2193 Select Item)",
        choices=[
            Choice(name="Android 11", value="11"),
            Choice(name="Android 13", value="13"),
            Choice(name="Exit", value=None)
        ],
        default="13",
    ).execute()
    if not android_version:
        exit()
    args.android_version = android_version
    action = inquirer.select(
        message="Please select an action",
        choices=[
            "Install",
            "Remove",
            "Hack",
            "Get Google Device ID to Get Certified"
        ],
        instruction="([↑↓]: Select Item)",
        default=None,
    ).execute()
    if not action:
        exit()

    install_choices = ["gapps", "microg", "libndk", "libhoudini", "magisk", "mitm", "smartdock", "fdroidpriv", "widevine",]
    hack_choices = []
    if android_version == "11":
        hack_choices.extend(["nodataperm", "hidestatusbar"])
    elif android_version == "13":
        hack_choices.extend(["nodataperm"])

    if action == "Install":
        apps = inquirer.checkbox(
            message="Select apps",
            instruction="([\u2191\u2193]: Select Item. [Space]: Toggle Choice), [Enter]: Confirm",
            validate=lambda result: len(result) >= 1,
            invalid_message="should be at least 1 selection",
            choices=install_choices
        ).execute()
        microg_variants = ["Standard", "NoGoolag",
                           "UNLP", "Minimal", "MinimalIAP"]
        if "microg" in apps:
            microg_variant = inquirer.select(
                message="Select MicroG variant",
                choices=microg_variants,
                default="Standard",
            ).execute()
            args.microg_variant = microg_variant
        args.app = apps
        install_app(args)
    elif action == "Remove":
        apps = inquirer.checkbox(
            message="Select apps",
            instruction="([\u2191\u2193]: Select Item. [Space]: Toggle Choice), [Enter]: Confirm",
            validate=lambda result: len(result) >= 1,
            invalid_message="should be at least 1 selection",
            choices=[*install_choices, *hack_choices]
        ).execute()
        args.app = apps
        args.microg_variant="Standard"
        remove_app(args)
    elif action == "Hack":
        apps = inquirer.checkbox(
            message="Select hack options",
            instruction="([\u2191\u2193]: Select Item. [Space]: Toggle Choice), [Enter]: Confirm",
            validate=lambda result: len(result) >= 1,
            invalid_message="should be at least 1 selection",
            choices=hack_choices
        ).execute()
        args.option_name = apps
        hack_option(args)
    elif action == "Get Google Device ID to Get Certified":
        AndroidId().get_id()


def _choose_one(prompt, choices):
    print(prompt)
    for i, c in enumerate(choices, 1):
        print("  {}. {}".format(i, c))
    while True:
        sel = input("> ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(choices):
            return choices[int(sel) - 1]
        print("Invalid selection, try again.")


def _choose_many(prompt, choices):
    print(prompt)
    for i, c in enumerate(choices, 1):
        print("  {}. {}".format(i, c))
    print("Enter numbers separated by spaces or commas")
    while True:
        raw = input("> ").strip()
        nums = [x for x in raw.replace(",", " ").split() if x.isdigit()]
        sel = [choices[int(n) - 1] for n in nums if 1 <= int(n) <= len(choices)]
        if sel:
            # preserve order, drop duplicates
            out = []
            for item in sel:
                if item not in out:
                    out.append(item)
            return out
        print("Invalid selection, try again.")


def interact_basic():
    os.system("clear")
    args = argparse.Namespace()
    android_version = _choose_one("Select Android version", ["11", "13"])
    if not android_version:
        return
    args.android_version = android_version

    action = _choose_one("Please select an action", [
        "Install",
        "Remove",
        "Hack",
        "Get Google Device ID to Get Certified"
    ])
    if not action:
        return

    install_choices = ["gapps", "microg", "libndk", "libhoudini", "magisk", "mitm",
                       "smartdock", "fdroidpriv", "widevine"]
    hack_choices = []
    if android_version == "11":
        hack_choices.extend(["nodataperm", "hidestatusbar"])
    elif android_version == "13":
        hack_choices.extend(["nodataperm"])

    if action == "Install":
        apps = _choose_many("Select apps", install_choices)
        microg_variants = ["Standard", "NoGoolag", "UNLP", "Minimal", "MinimalIAP"]
        if "microg" in apps:
            microg_variant = _choose_one("Select MicroG variant", microg_variants)
            args.microg_variant = microg_variant
        else:
            args.microg_variant = "Standard"
        args.app = apps
        install_app(args)
    elif action == "Remove":
        apps = _choose_many("Select apps", [*install_choices, *hack_choices])
        args.app = apps
        args.microg_variant = "Standard"
        remove_app(args)
    elif action == "Hack":
        apps = _choose_many("Select hack options", hack_choices)
        args.option_name = apps
        hack_option(args)
    elif action == "Get Google Device ID to Get Certified":
        AndroidId().get_id()


def interact():
    if HAS_INQUIRER:
        interact_fancy()
    else:
        interact_basic()


def main():
    parser = argparse.ArgumentParser(description='''
    Does stuff like installing Gapps, installing Magisk, installing NDK Translation and getting Android ID for device registration.
    Use -h  flag for help!''')

    subparsers = parser.add_subparsers(title="coomand", dest='command')
    parser.add_argument('-a', '--android-version',
                        dest='android_version',
                        help='Specify the Android version',
                        default="13",
                        choices=["11", "13"])

    # android command
    certified = subparsers.add_parser(
        'certified', help='Get device ID to obtain Play Store certification')
    certified.set_defaults(func=get_certified)

    status_parser = subparsers.add_parser(
        'status', help='Show installed extras and hacks')
    status_parser.set_defaults(func=status_app)

    backup_parser = subparsers.add_parser(
        'backup', help='Backup Waydroid images')
    backup_parser.set_defaults(func=backup_images)

    restore_parser = subparsers.add_parser(
        'restore', help='Restore the latest Waydroid image backup')
    restore_parser.set_defaults(func=restore_images)

    install_choices = ["gapps", "microg", "libndk", "libhoudini",
                       "magisk", "mitm", "smartdock", "widevine", "fdroidpriv"]
    hack_choices = ["nodataperm", "hidestatusbar"]
    micrg_variants = ["Standard", "NoGoolag", "UNLP", "Minimal", "MinimalIAP"]
    remove_choices = install_choices

    arg_template = {
        "dest": "app",
        "type": str,
        "nargs": '+',
        # "metavar":"",
    }

    install_help = """
gapps: Install Open GApps (Android 11) or MindTheGapps (Android 13)
microg: Add microG, Aurora Store and Aurora Droid to WayDriod
libndk: Add libndk arm translation, better for AMD CPUs
libhoudini: Add libhoudini arm translation, better for Intel CPUs
magisk: Install Magisk Delta to WayDroid
mitm -c CA_CERT_FILE: Install root CA cert into system trust store
smartdock: A desktop mode launcher for Android
widevine: Add support for widevine DRM L3
    """
    # install and its aliases
    install_parser = subparsers.add_parser(
        'install', formatter_class=argparse.RawTextHelpFormatter, help='Install an app')
    install_parser.add_argument(
        **arg_template, choices=install_choices, help=install_help)
    install_parser.add_argument('-c', '--ca-cert',
                                dest='ca_cert_file',
                                help='[for mitm only] The CA certificate file (*.pem) to install',
                                default=None)
    install_parser.set_defaults(func=install_app)

    # remove and its aliases
    remove_parser = subparsers.add_parser(
        'remove', aliases=["uninstall"], help='Remove an app')
    remove_parser.add_argument(
        **arg_template, choices=[*remove_choices, * hack_choices], help='Name of app to remove')
    remove_parser.set_defaults(func=remove_app)

    # hack and its aliases
    hack_parser = subparsers.add_parser('hack', help='Hack the system')
    hack_parser.add_argument(
        'option_name', nargs="+", choices=hack_choices, help='Name of hack option')
    hack_parser.set_defaults(func=hack_option)

    args = parser.parse_args()
    args.microg_variant = "Standard"
    if hasattr(args, 'func'):
        args_dict = vars(args)
        helper.check_root()
        args.func(args)
    else:
        helper.check_root()
        interact()


if __name__ == "__main__":
    main()
