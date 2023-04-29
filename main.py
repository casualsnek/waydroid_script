#!/usr/bin/env python3

import argparse
import os
from typing import List
from stuffs.android_id import AndroidId
from stuffs.gapps import Gapps
from stuffs.general import General
from stuffs.hidestatusbar import HideStatusBar
from stuffs.houdini import Houdini
from stuffs.magisk import Magisk
from stuffs.microg import MicroG
from stuffs.ndk import Ndk
from stuffs.nodataperm import Nodataperm
from stuffs.smartdock import Smartdock
from stuffs.widevine import Widevine
import tools.helper as helper
from tools import container
from tools import images

import argparse

from tools.logger import Logger


def get_certified():
    AndroidId.get_id()


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


def main():

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
            install_list.append(MicroG(args.android_version))

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
            remove_list.append(MicroG(args.android_version))
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
        Logger.warning("If these hacks cause any problems, run `sudo python main.py remove <hack_option>` to remove")

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

    install_choices = ["gapps", "microg", "libndk",
                       "libhoudini", "magisk", "smartdock", "widevine"]
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
smartdock: A desktop mode launcher for Android
widevine: Add support for widevine DRM L3
    """
    # install and its aliases
    install_parser = subparsers.add_parser(
        'install', formatter_class=argparse.RawTextHelpFormatter, help='Install an app')
    install_parser.add_argument(
        **arg_template, choices=install_choices, help=install_help)
    install_parser.set_defaults(func=install_app)

    # remove and its aliases
    remove_parser = subparsers.add_parser('remove',aliases=["uninstall"], help='Remove an app')
    remove_parser.add_argument(
        **arg_template, choices=[*remove_choices,* hack_choices], help='Name of app to remove')
    remove_parser.set_defaults(func=remove_app)

    # hack and its aliases
    hack_parser = subparsers.add_parser('hack', help='Hack the system')
    hack_parser.add_argument(
        'option_name',nargs="+" , choices=hack_choices, help='Name of hack option')
    hack_parser.set_defaults(func=hack_option)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args_dict = vars(args)
        helper.check_root()
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
