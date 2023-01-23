import re
import dbus
from tools.helper import run

def DBusContainerService(object_path="/ContainerManager", intf="id.waydro.ContainerManager"):
    return dbus.Interface(dbus.SystemBus().get_object("id.waydro.Container", object_path), intf)

def DBusSessionService(object_path="/SessionManager", intf="id.waydro.SessionManager"):
    return dbus.Interface(dbus.SessionBus().get_object("id.waydro.Session", object_path), intf)

def use_dbus():
    try:
        DBusContainerService()
    except:
        return False
    return True

def use_overlayfs():
    # with open("/var/lib/waydroid/waydroid.cfg") as f:
    #         cont=f.read()
    #         if re.search("mount_overlays[ \t]*=[ \t]*True", cont):
    #             return True
    #         return False
    return False

def get_session():
    return DBusContainerService().GetSession()

def stop():
    if use_dbus():
        session = DBusContainerService().GetSession()
        if session:
            DBusContainerService().Stop(False)
    else:
        run(["waydroid", "container", "stop"])

def start(*session):
    if use_dbus() and session:
        DBusContainerService().Start(session[0])
    else:
        run(["systemctl", "restart", "waydroid-container.service"])        

def is_running():
    if use_dbus():
        if DBusContainerService().GetSession():
            return True
        return False
    else:
        return "Session:\tRUNNING" in run(["waydroid", "status"]).stdout.decode()



