#!/usr/bin/env python3

import argparse
from logging import Logger
from stuffs.android_id import AndroidId
from stuffs.gapps import Gapps
from stuffs.hidestatusbar import HideStatusBar
from stuffs.houdini import Houdini
from stuffs.magisk import Magisk
from stuffs.microg import MicroG
from stuffs.ndk import Ndk
from stuffs.nodataperm import Nodataperm
from stuffs.smartdock import Smartdock
from stuffs.widevine import Widevine
import tools.helper as helper
def install(*args):
    if "gapps" in args:
        Gapps().install()
    if "libndk" in args and "houdini" not in args:
        arch = helper.host()[0]
        if arch == "x86_64":
            Ndk().install()
        else:
            Logger.warn("libndk is not supported on your CPU")
    if "libhoudini" in args and "ndk" not in args:
        arch = helper.host()[0]
        if arch == "x86_64":
            Houdini().install()
        else:
            Logger.warn("libhoudini is not supported on your CPU")
    if "magisk" in args:
        Magisk().install()
    if "widevine" in args:
        Widevine().install()
    if "smartdock" in args:
        Smartdock().install()
    if "nodataperm" in args:
        Nodataperm().install()
    if "microg" in args:
        MicroG().install()
    if "hidestatus" in args:
        HideStatusBar().install()

def uninstall(*args):
    if "gapps" in args:
        Gapps().uninstall()
    if "libndk" in args:
        Ndk().uninstall()
    if "libhoudini" in args:
        Houdini().uninstall()
    if "magisk" in args:
        Magisk().uninstall()
    if "widevine" in args:
        Widevine().uninstall()
    if "smartdock" in args:
        Smartdock().uninstall()
    if "nodataperm" in args:
        Nodataperm().uninstall()
    if "microg" in args:
        MicroG().uninstall()
    if "hidestatus" in args:
        HideStatusBar().uninstall()

def main():
    about = """
    WayDroid Helper script v0.3
    Does stuff like installing Gapps, installing Magisk, installing NDK Translation and getting Android ID for device registration.
    Use -h  flag for help!
    """
    helper.check_root()

    parser = argparse.ArgumentParser(prog=about)
    parser.set_defaults(app="")

    subparsers = parser.add_subparsers(title="subcommands", help="operations")

    google_id_parser=subparsers.add_parser('google',
                        help='grab device id for unblocking Google Apps')
    google_id_parser.set_defaults(func=AndroidId().get_id)
    # create the parser for the "a" command

    arg_template = {
        "dest": "app",
        "type": str,
        "nargs": '+',
        "metavar":"",
        "choices": ["gapps", "microg", "libndk", "libhoudini", "magisk", "smartdock", "widevine", "nodataperm", "hidestatus"],
    }

    install_help = """
gapps: Install Open GApps Pico(minimum GApps installation)
microg: Add microG, Aurora Store and Aurora Droid to WayDriod
libndk: Add libndk arm translation, better for AMD CPUs
libhoudini: Add libhoudini arm translation, better for Intel CPUs
magisk: Install Magisk Delta to WayDroid
smartdock: A desktop mode launcher for Android
    """
    install_parser = subparsers.add_parser("install",formatter_class=argparse.RawTextHelpFormatter, help='install something')
    install_parser.set_defaults(func=install)
    install_parser.add_argument(**arg_template,help=install_help)

    uninstall_parser = subparsers.add_parser("uninstall", help='uninstall something')
    uninstall_parser.set_defaults(func=uninstall)
    uninstall_parser.add_argument(**arg_template)

    args = parser.parse_args()

    if args.app:
        args.func(*args.app)
    else:
        args.func()

    

if __name__ == "__main__":
    main()
