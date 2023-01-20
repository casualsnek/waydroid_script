import argparse
from logging import Logger
from stuffs.android_id import Android_id
from stuffs.gapps import Gapps
from stuffs.houdini import Houdini
from stuffs.magisk import Magisk
from stuffs.ndk import Ndk
from stuffs.widevine import Widevine
import tools.helper as helper


def main():
    about = """
    WayDroid Helper script v0.3
    Does stuff like installing Gapps, Installing NDK Translation and getting Android ID for device registration.
    Use -h  flag for help !
    """
    helper.check_root()
    parser = argparse.ArgumentParser(description=about, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-g', '--install-gapps',
                        dest='gapps',
                        help='Install OpenGapps to waydroid',
                        action='store_true')
    parser.add_argument('-n', '--install-ndk-translation',
                        dest='ndk',
                        help='Install libndk translation for arm translation',
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
    if args.getid:
       Android_id().get_id() 
    if args.gapps:
        Gapps().install()
    if args.ndk and not args.houdini:
        arch = helper.host()[0]
        if arch == "x86_64":
            Ndk().install()
        else:
            Logger.warn("libndk is not supported on your CPU")
    if args.houdini and not args.ndk:
        arch = helper.host()[0]
        if arch == "x86_64":
            Houdini().install()
        else:
            Logger.warn("libhoudini is not supported on your CPU")
    if args.magisk:
        Magisk().install()
    if args.widevine:
        Widevine().install()

if __name__ == "__main__":
    main()