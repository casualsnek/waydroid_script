# Waydroid Extras Script

Script to add Google Apps, microG, Magisk, ARM translation, Widevine and other extras to Waydroid.

This fork (`BENDER35/waydroid_script_2026`) keeps the original `casualsnek/waydroid_script` workflow and fixes several issues found while testing on current systems.

## Features

- Install / remove OpenGApps (Android 11) or MindTheGapps (Android 13)
- Install / remove microG (Standard, NoGoolag, UNLP, Minimal, MinimalIAP)
- Install / remove libndk ARM translation (recommended for AMD CPUs)
- Install / remove libhoudini ARM translation (recommended for Intel CPUs)
- Install / remove Magisk Delta
- Install / remove Widevine DRM L3
- Install / remove Smart Dock
- Install / remove F-Droid Privileged Extension
- Install a self-signed CA certificate into the system trust store (`mitm`)
- Hacks: `nodataperm`, `hidestatusbar`
- Get the Android ID required to certify a device with Google

## Requirements

- Waydroid initialized and working
- Python 3
- `lzip`
- Python packages: `requests`, `tqdm`, `InquirerPy`

On Debian / Ubuntu:

```bash
sudo apt install lzip python3 python3-pip
```

## Installation

```bash
git clone https://github.com/BENDER35/waydroid_script_2026.git
cd waydroid_script_2026
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

## Usage

### Interactive mode

```bash
sudo venv/bin/python3 main.py
```

### Command line

```bash
# Get the Android ID for Play Store certification
sudo venv/bin/python3 main.py certified

# Install one or more extras
sudo venv/bin/python3 main.py install gapps
sudo venv/bin/python3 main.py install microg magisk libndk
sudo venv/bin/python3 main.py install mitm --ca-cert mycert.pem
sudo venv/bin/python3 main.py install fdroidpriv

# Remove one or more extras
sudo venv/bin/python3 main.py remove gapps
sudo venv/bin/python3 main.py uninstall microg magisk

# Apply hacks (Android 11; nodataperm is also available on Android 13)
sudo venv/bin/python3 main.py hack nodataperm
sudo venv/bin/python3 main.py hack hidestatusbar
```

Android version can be selected with `-a` / `--android-version` (default: 13):

```bash
sudo venv/bin/python3 main.py -a 11 install gapps
```

## Dependencies

`lzip` is required for OpenGApps extraction. Install it with your distribution package manager:

- Arch / Manjaro: `sudo pacman -S lzip`
- Debian / Ubuntu: `sudo apt install lzip`
- Fedora / RHEL: `sudo dnf install lzip`
- openSUSE: `sudo zypper install lzip`

## Notes

- The script must be run as root.
- On non-overlayfs setups the script mounts the Waydroid images under `/tmp/waydroid`; make sure Waydroid is stopped before running it.
- Magisk is installed on the next boot.
- For Google Play certification, run `certified`, register the printed ID at https://google.com/android/uncertified/, wait 10-20 minutes, then clear Google Play Services cache.

## Troubleshooting

- `ModuleNotFoundError: No module named 'InquirerPy'`: install the requirements inside the virtual environment (`venv/bin/pip install -r requirements.txt`).
- Waydroid must be running for `certified`.
- If a hack breaks boot, remove it with `sudo venv/bin/python3 main.py remove <hack>`.

## Credits

- [WayDroid](https://github.com/waydroid/waydroid)
- [casualsnek/waydroid_script](https://github.com/casualsnek/waydroid_script)
- [Magisk Delta](https://huskydg.github.io/magisk-files/)
- [microG Project](https://microg.org)
- [Open GApps](https://opengapps.org)
- [Smart Dock](https://github.com/axel358/smartdock)
- [wd-scripts](https://github.com/electrikjesus/wd-scripts/)