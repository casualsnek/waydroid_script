import os
import shutil
from stuff.general import General

class Smartdock(General):
    id = "smartdock"
    dl_link = "https://f-droid.org/repo/cu.axel.smartdock_198.apk"
    partition = "system"
    dl_file_name = "smartdock.apk"
    act_md5 = "a8ce0bca5e1772796404602e0fa250a4"
    apply_props = { "qemu.hw.mainkeys" : "1" }
    skip_extract = True
    permissions = """<?xml version="1.0" encoding="utf-8"?>
<permissions>
    <privapp-permissions package="cu.axel.smartdock">
	    <permission name="android.permission.SYSTEM_ALERT_WINDOW" />
	    <permission name="android.permission.GET_TASKS"/>
	    <permission name="android.permission.REORDER_TASKS"/>
        <permission name="android.permission.REMOVE_TASKS" />
        <permission name="android.permission.ACCESS_WIFI_STATE"/>
	    <permission name="android.permission.CHANGE_WIFI_STATE"/>
        <permission name="android.permission.ACCESS_NETWORK_STATE"/>
        <permission name="android.permission.ACCESS_FINE_LOCATION"/>
        <permission name="android.permission.READ_EXTERNAL_STORAGE"/>
        <permission name="android.permission.MANAGE_USERS"/>
        <permission name="android.permission.BLUETOOTH_ADMIN"/>
        <permission name="android.permission.BLUETOOTH_CONNECT"/>
        <permission name="android.permission.BLUETOOTH"/>
	    <permission name="android.permission.REQUEST_DELETE_PACKAGES"/>
        <permission name="android.permission.ACCESS_SUPERUSER"/>
        <permission name="android.permission.PACKAGE_USAGE_STATS" />
        <permission name="android.permission.QUERY_ALL_PACKAGES" />
    </privapp-permissions>
</permissions>
    """
    files = [
            "etc/permissions/permissions_cu.axel.smartdock.xml",
            "priv-app/SmartDock",
            "etc/init/smartdock.rc"
        ]
    rc_content = '''
on property:sys.boot_completed=1
    start set_home_activity

service set_home_activity /system/bin/sh -c "cmd package set-home-activity cu.axel.smartdock/.activities.LauncherActivity"
    user root
    group root
    oneshot
    '''

    def copy(self):
        if not os.path.exists(os.path.join(self.copy_dir, self.partition, "priv-app", "SmartDock")):
            os.makedirs(os.path.join(self.copy_dir, self.partition, "priv-app", "SmartDock"))
        if not os.path.exists(os.path.join(self.copy_dir, self.partition, "etc", "permissions")):
            os.makedirs(os.path.join(self.copy_dir, self.partition, "etc", "permissions"))
        shutil.copyfile(os.path.join(self.download_loc),
                        os.path.join(self.copy_dir, self.partition, "priv-app/SmartDock/smartdock.apk"))
        
        with open(os.path.join(self.copy_dir, self.partition, "etc", "permissions", "permissions_cu.axel.smartdock.xml"), "w") as f:
            f.write(self.permissions)

        rc_dir = os.path.join(self.copy_dir, self.partition, "etc/init/smartdock.rc")
        if not os.path.exists(os.path.dirname(rc_dir)):
            os.makedirs(os.path.dirname(rc_dir))
        self.extract_app_lib(os.path.join(self.copy_dir, self.partition, "priv-app/SmartDock/smartdock.apk"))
        with open(rc_dir, "w") as f:
            f.write(self.rc_content)
