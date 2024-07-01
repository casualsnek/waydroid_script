# Waydroid Extras Script

Script to add GApps and other stuff to Waydroid!

# Installation/Usage

## Interactive terminal interface

```
git clone https://github.com/casualsnek/waydroid_script
cd waydroid_script
python3 -m venv venv
venv/bin/pip install -r requirements.txt
sudo venv/bin/python3 main.py
```

![image-20230430013103883](assets/img/README/image-20230430013103883.png)

![image-20230430013119763](assets/img/README/image-20230430013119763.png)

![image-20230430013148814](assets/img/README/image-20230430013148814.png)

## Command line

```bash
git clone https://github.com/casualsnek/waydroid_script
cd waydroid_script
python3 -m venv venv
venv/bin/pip install -r requirements.txt
# install something
sudo venv/bin/python3 main.py install {gapps, magisk, libndk, libhoudini, nodataperm, smartdock, microg, mitm}
# uninstall something
sudo venv/bin/python3 main.py uninstall {gapps, magisk, libndk, libhoudini, nodataperm, smartdock, microg}
# get Android device ID
sudo venv/bin/python3 main.py certified
# some hacks
sudo venv/bin/python3 main.py hack {nodataperm, hidestatusbar}
```

## Dependencies

"lzip" is required for this script to work, install it using your distribution's package manager:

### Arch, Manjaro, and EndeavourOS-based distributions:

	sudo pacman -S lzip

### Debian and Ubuntu-based distributions:

	sudo apt install lzip

### RHEL, Fedora, and Rocky-based distributions:

	sudo dnf install lzip

### openSUSE-based distributions:

	sudo zypper install lzip

## Install Open GApps

![](assets/1.png)

Open the terminal and switch to the directory where "main.py" is located, then run:

    sudo venv/bin/python3 main.py install gapps

Then launch Waydroid with:

    waydroid show-full-ui

After Waydroid has finished booting, open the terminal and switch to the directory where "main.py" is located, then run:

    sudo python3 main.py google

Copy the returned numeric ID, then
open ["https://google.com/android/uncertified/?pli=1"](https://google.com/android/uncertified/?pli=1). Enter the ID and
register it. Wait 10–20 minutes for the device to get registered. Then clear Google Play Service's cache and try logging
in!

## Install Magisk

![](assets/2.png)

Open the terminal and switch to the directory where "main.py" is located, then run:

    sudo venv/bin/python3 main.py install magisk

Magisk will be installed on next boot!

Zygisk and modules like LSPosed should work now.

If you want to update Magisk, Please use `Direct Install into system partition` or run this script again.

This script only focuses on Magisk installation, if you need more management, please
check https://github.com/nitanmarcel/waydroid-magisk

## Install libndk ARM translation

libndk_translation from guybrush firmware.

libndk seems to have better performance than libhoudini on AMD.

Open the terminal and switch to the directory where "main.py" is located, then run:

    sudo venv/bin/python3 main.py install libndk

## Install libhoudini ARM translation

Intel's libhoudini for intel/AMD x86 CPU, pulled from Microsoft's WSA 11 image

houdini version: 11.0.1b_y.38765.m

houdini64 version: 11.0.1b_z.38765.m

Open the terminal and switch to the directory where "main.py" is located, then run:

    sudo venv/bin/python3 main.py install libhoudini

## Integrate Widevine DRM (L3)

![](assets/3.png)

Open the terminal and switch to the directory where "main.py" is located, then run:

    sudo venv/bin/python3 main.py install widevine

## Install Smart Dock

![](assets/4.png)
![](assets/5.png)

Open the terminal and switch to the directory where "main.py" is located, then run:

    sudo venv/bin/python3 main.py install smartdock

## Install a self-signed CA certificate

Open the terminal and switch to the directory where "main.py" is located, then run:

    sudo venv/bin/python3 main.py install mitm --ca-cert mycert.pem

## Granting full permission for apps data (HACK)

This is a temporary hack to combat against the apps permission issue on Android 11. Whenever an app is open, it will
always enable a property (persist.sys.nodataperm) to make it execute a script to grant the data full permissions (777).
The **correct** way is to use `sdcardfs` or `esdfs`, both need to recompile the kernel or WayDroid image.

Arknights, PUNISHING: GRAY RAVEN, and other games won't freeze on the black screen.

![](assets/6.png)

Open the terminal and switch to the directory where "main.py" is located, then run:

```
sudo venv/bin/python3 main.py hack nodataperm
```

**WARNING**: Tested on `lineage-18.1-20230128-VANILLA-waydroid_x86_64.img`. This script will
replace `/system/framework/service.jar`, which may prevent Waydroid from booting. If so,
run `sudo venv/bin/python3 main.py uninstall nodataperm` to remove it.

Or you can run the following commands directly in `sudo waydroid shell`. In this way, every time a new game is
installed, you need to run it again, but it is much less risky.

```
chmod 777 -R /sdcard/Android
chmod 777 -R /data/media/0/Android 
chmod 777 -R /sdcard/Android/data
chmod 777 -R /data/media/0/Android/obb 
chmod 777 -R /mnt/*/*/*/*/Android/data
chmod 777 -R /mnt/*/*/*/*/Android/obb
```

- https://github.com/supremegamers/device_generic_common/commit/2d47891376c96011b2ee3c1ccef61cb48e15aed6
- https://github.com/supremegamers/android_frameworks_base/commit/24a08bf800b2e461356a9d67d04572bb10b0e819

## Install microG, Aurora Store, and Aurora Droid

![](assets/7.png)

```
sudo python main.py install microg
```

## Hide status bar

Before
![Before](assets/8.png)

After
![After](assets/9.png)

```
sudo venv/bin/python3 main.py hack hidestatusbar
```

## Get Android ID for device registration

You need to register your device with its ID before being able to use GApps, this will print out your Android ID, which
you can use for device registration required for Google apps:
Open the terminal and switch to the directory where "main.py" is located, then run:

    sudo venv/bin/python3 main.py certified

Star this repository if you find this useful, if you encounter a problem, create an issue on GitHub!

## Error handling

- Magisk installed: N/A

Check [waydroid-magisk](https://github.com/nitanmarcel/waydroid-magisk)

## Credits

- [Waydroid](https://github.com/waydroid/waydroid)
- [Magisk Delta](https://huskydg.github.io/magisk-files)
- [microG Project](https://microg.org)
- [Open GApps](https://opengapps.org)
- [Smart Dock](https://github.com/axel358/smartdock)
- [wd-scripts](https://github.com/electrikjesus/wd-scripts)
