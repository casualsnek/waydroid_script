#!/usr/bin/env python3
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
import argparse
import os
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


def get_certified(args):
    AndroidId().get_id()


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

    for item in remove_list:
        item.uninstall()

    if not container.use_overlayfs():
        umount("vendor", copy_dir)
        umount("system", copy_dir)

    container.upgrade()


def hack_option(args):
    Logger.warning(
        "If these hacks cause any problems, run `sudo python main.py remove <hack_option>` to remove")

    hack_list: List[General] = []
    options = args.option_name
    if "nodataperm" in options:
        hack_list.append(Nodataperm())
    if "hidestatusbar" in options:
        hack_list.append(HideStatusBar())

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


def interact():
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
        default="11",
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

    install_choices = ["gapps", "microg", "libndk", "magisk", "smartdock", "fdroidpriv",]
    hack_choices = []
    if android_version=="11":
        install_choices.extend(["libhoudini", "widevine"])
        hack_choices.extend(["nodataperm", "hidestatusbar"])

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


def main():
    parser = argparse.ArgumentParser(description='''
    Does stuff like installing Gapps, installing Magisk, installing NDK Translation and getting Android ID for device registration.
    Use -h  flag for help!''')

    subparsers = parser.add_subparsers(title="coomand", dest='command')
    parser.add_argument('-a', '--android-version',
                        dest='android_version',
                        help='Specify the Android version',
                        default="11",
                        choices=["11", "13"])

    # android command
    certified = subparsers.add_parser(
        'certified', help='Get device ID to obtain Play Store certification')
    certified.set_defaults(func=get_certified)

    install_choices = ["gapps", "microg", "libndk", "libhoudini",
                       "magisk", "mitm", "smartdock", "widevine"]
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
