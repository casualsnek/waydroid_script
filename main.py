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


import argparse

# def main():
#     def get_certified():
#         print("Calling android_get_certified function")

#     def install_app(app_name):
#         print(f"Installing {app_name}")

#     def remove_app(app_name):
#         print(f"Removing {app_name}")

#     def hack_option(option_name):
#         print(f"Enabling {option_name}")

#     parser = argparse.ArgumentParser(description='''
#     Does stuff like installing Gapps, installing Magisk, installing NDK Translation and getting Android ID for device registration.
#     Use -h  flag for help!''')

#     subparsers = parser.add_subparsers(dest='command')

#     # android command
#     certified = subparsers.add_parser('certified', help='Get device ID to obtain Play Store certification')
#     certified.set_defaults(func=get_certified)

#     install_choices=["gapps", "microg", "libndk", "libhoudini", "magisk", "smartdock", "widevine"],
#     hack_choices = ["nodataperm", "hidestatusbar"]
#     remove_choices=install_choices

#     arg_template = {
#         "dest": "app",
#         "type": str,
#         "nargs": '+',
#         "metavar":"",
#     }

#     install_help = """
# gapps: Install Open GApps (Android 11) or MindTheGapps (Android 13)
# microg: Add microG, Aurora Store and Aurora Droid to WayDriod
# libndk: Add libndk arm translation, better for AMD CPUs
# libhoudini: Add libhoudini arm translation, better for Intel CPUs
# magisk: Install Magisk Delta to WayDroid
# smartdock: A desktop mode launcher for Android
# widevine: Add support for widevine DRM L3
#     """
#     # install and its aliases
#     install_parser = subparsers.add_parser('install', aliases=['-i'], formatter_class=argparse.RawTextHelpFormatter, help='Install an app')
#     install_parser.add_argument(**arg_template, help=install_help)
#     install_parser.set_defaults(func=install_app)

#     # remove and its aliases
#     remove_parser = subparsers.add_parser('remove', aliases=['-r'], help='Remove an app')
#     remove_parser.add_argument(**arg_template, help='Name of app to remove')
#     remove_parser.set_defaults(func=remove_app)

#     # hack and its aliases
#     hack_parser = subparsers.add_parser('hack', aliases=['-h'], help='Hack the system')
#     hack_parser.add_argument('option_name', choices=["nodataperm", "hidestatus"], help='Name of hack option')
#     hack_parser.set_defaults(func=hack_option)

#     args = parser.parse_args()
#     if hasattr(args, 'func'):
#         args_dict = vars(args)
#         if 'app_name' in args_dict:
#             args.func(args_dict['app_name'])
#         else:
#             args.func(args_dict['option_name'])
#     else:
#         parser.print_help()





def install(args):
    app = args.app
    if "gapps" in app:
        Gapps(args.android_version).install()
    if "libndk" in app and "houdini" not in app:
        arch = helper.host()[0]
        if arch == "x86_64":
            Ndk(args.android_version).install()
        else:
            Logger.warn("libndk is not supported on your CPU")
    if "libhoudini" in app and "ndk" not in app:
        arch = helper.host()[0]
        if arch == "x86_64":
            Houdini(args.android_version).install()
        else:
            Logger.warn("libhoudini is not supported on your CPU")
    if "magisk" in app:
        Magisk().install()
    if "widevine" in app:
        Widevine(args.android_version).install()
    if "smartdock" in app:
        Smartdock().install()
    if "nodataperm" in app:
        Nodataperm().install()
    if "microg" in app:
        MicroG().install()
    if "hidestatus" in app:
        HideStatusBar().install()

def uninstall(args):
    app = args.app
    if "gapps" in app:
        Gapps(args.android_version).uninstall()
    if "libndk" in app:
        Ndk(args.android_version).uninstall()
    if "libhoudini" in app:
        Houdini(args.android_version).uninstall()
    if "magisk" in app:
        Magisk().uninstall()
    if "widevine" in app:
        Widevine(args.android_version).uninstall()
    if "smartdock" in app:
        Smartdock().uninstall()
    if "nodataperm" in app:
        Nodataperm().uninstall()
    if "microg" in app:
        MicroG().uninstall()
    if "hidestatus" in app:
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
    parser.add_argument('-a', '--android-version',
                        dest='android_version',
                        help='Specify the Android version',
                        default="11",
                        choices=["11","13"])
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

    install_parser = subparsers.add_parser("install",formatter_class=argparse.RawTextHelpFormatter, help='install something')
    install_parser.set_defaults(func=install)
    install_parser.add_argument(**arg_template,help=install_help)

    uninstall_parser = subparsers.add_parser("uninstall", help='uninstall something')
    uninstall_parser.set_defaults(func=uninstall)
    uninstall_parser.add_argument(**arg_template)

    args = parser.parse_args()
    if args.app:
        args.func(args)
    else:
        args.func()

    

if __name__ == "__main__":
    main()
