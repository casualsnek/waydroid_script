import configparser
import os
import sys
# import dbus
from tools.helper import run
from tools.logger import Logger

# def DBusContainerService(object_path="/ContainerManager", intf="id.waydro.ContainerManager"):
#     return dbus.Interface(dbus.SystemBus().get_object("id.waydro.Container", object_path), intf)

# def DBusSessionService(object_path="/SessionManager", intf="id.waydro.SessionManager"):
#     return dbus.Interface(dbus.SessionBus().get_object("id.waydro.Session", object_path), intf)

# def use_dbus():
#     try:
#         DBusContainerService()
#     except:
#         return False
#     return True

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


# def get_session():
#     return DBusContainerService().GetSession()

def stop():
    # if use_dbus():
    #     session = DBusContainerService().GetSession()
    #     if session:
    #         DBusContainerService().Stop(False)
    # else:
        run(["waydroid", "container", "stop"])


def is_running():
        return "Session:\tRUNNING" in run(["waydroid", "status"]).stdout.decode()

def upgrade():
    run(["waydroid", "upgrade", "-o"], ignore=r"\[.*\] Stopping container\n\[.*\] Starting container")