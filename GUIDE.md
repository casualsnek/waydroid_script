# Waydroid Extras Script – How it works

This guide explains the internal workflow of `main.py` and its helper modules.

## Prerequisite: Wayland

Waydroid only runs on a Wayland session. Check with `echo $XDG_SESSION_TYPE`. If it prints `x11`, switch to a Wayland session or use a nested compositor (`weston`/`cage`). When using `sudo`, preserve the environment with `sudo -E`.

## Overview

`main.py` is a Python script that modifies Waydroid images (mainly `system.img` and `vendor.img`) to add extras such as Google Apps, microG, Magisk, ARM translation, Widevine, and more.

Two usage modes:

1. **Interactive mode**: run `sudo python3 main.py` without arguments; menus are powered by `InquirerPy`.
2. **Command line mode**: subcommands `install`, `remove`/`uninstall`, `hack`, `certified`.

## Main files

- `main.py`: entry point, argument parsing, orchestration.
- `stuff/*.py`: implementation of each extra.
- `stuff/general.py`: base `General` class (download, extract, copy, permissions, properties).
- `tools/container.py`: overlayfs detection, container start/stop, upgrade.
- `tools/images.py`: mount/umount/resize of images.
- `tools/helper.py`: command execution, downloads, architecture detection.
- `tools/logger.py`: colored output.

## Install flow

1. Build list of extra objects.
2. If not using overlayfs: stop Waydroid, resize images if needed, mount them under `/tmp/waydroid`.
3. Download package (cached if present).
4. Extract.
5. Copy files into mounted image or overlay.
6. Fix permissions.
7. Apply properties in `waydroid.cfg` when applicable.
8. If not using overlayfs: unmount images.
9. Run `waydroid upgrade -o`.

## Uninstall flow

1. Build list of extras to remove.
2. If not using overlayfs: mount images.
3. Remove listed files.
4. Remove associated properties.
5. Fix permissions.
6. If not using overlayfs: unmount images.
7. Run `waydroid upgrade -o`.

## Overlayfs vs. non-overlayfs

- With `mount_overlays = True` in `/var/lib/waydroid/waydroid.cfg`, changes go to `/var/lib/waydroid/overlay` without mounting images.
- Otherwise the script mounts `system.img` and `vendor.img` directly.

## Hacks

- `nodataperm`: replaces `services.jar` to grant full data permissions (Android 11/13).
- `hidestatusbar`: installs an overlay APK to hide the status bar (Android 11).

## Python dependency

Interactive menus require `InquirerPy`. Install requirements with:

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

## Safety notes

- Always run as root.
- Back up images before modifying them.
- If a hack breaks boot, remove it with `remove`.