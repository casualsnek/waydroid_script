import os
import sys
from tools import container
from tools.helper import run
from tools.logger import Logger


class Android_id:
   def get_id(self):

        if container.is_running():
            queryout = run([
                'waydroid','shell',
                'sqlite3',
                '/data/data/com.google.android.gsf/databases/gservices.db',
                "select * from main where name = \"android_id\";"
            ])
        else:
            Logger.error("Cannot access gservices.db, make sure gapps is installed and waydroid was started at least once after installation and make sure waydroid is running !")
            return
        print(queryout.stdout.decode().replace("android_id|", "").strip())
        print("   ^----- Open https://google.com/android/uncertified/?pli=1")
        print("          Login with your google id then submit the form with id shown above")
