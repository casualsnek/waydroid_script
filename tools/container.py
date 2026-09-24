import configparser
import os
import sys
from tools.helper import run
from tools.logger import Logger

def use_overlayfs():
    cfg = configparser.ConfigParser()
    cfg_file = os.environ.get("WAYDROID_CONFIG", "/var/lib/waydroid/waydroid.cfg")
    if not os.path.isfile(cfg_file):
        Logger.error("Cannot locate waydroid config file, reinit wayland and try again!")
        sys.exit(1)
    cfg.read(cfg_file)
    if "waydroid" not in cfg:
        Logger.error("Required entry in config was not found, Cannot continue!")
    if "mount_overlays" not in cfg["waydroid"]:
        return False
    if cfg["waydroid"]["mount_overlays"]=="True":
        return True
    return False


def stop():
        run(["waydroid", "container", "stop"])

def is_running():
        return "Session:\tRUNNING" in run(["waydroid", "status"]).stdout.decode()

def upgrade():
    try:
        run(["waydroid", "upgrade"], ignore=r"\[.*\] Stopping container\n\[.*\] Starting container")
    except subprocess.CalledProcessError:
        Logger.warning("Waydroid upgrade reported an error (likely system_ota), but we are continuing...")