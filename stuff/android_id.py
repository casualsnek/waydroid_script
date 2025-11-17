from tools import container
from tools.helper import shell
from tools.logger import Logger
import re

class AndroidId:
    def get_id(self):
        if not container.is_running():
            Logger.error("Please make sure Waydroid is running and Gapps has been installed!")
            return

        try:
            # Get list of user IDs and their names using 'pm list users'
            users_raw = shell(
                arg="pm list users",
                env="ANDROID_RUNTIME_ROOT=/apex/com.android.runtime ANDROID_DATA=/data ANDROID_TZDATA_ROOT=/apex/com.android.tzdata ANDROID_I18N_ROOT=/apex/com.android.i18n"
            )
            user_map = {}
            for line in users_raw.strip().splitlines():
                match = re.search(r'UserInfo\{(\d+):([^:}]+)', line)
                if match:
                    user_id, username = match.groups()
                    user_map[user_id] = username
        except Exception as e:
            Logger.error(f"Failed to parse user list: {e}")
            return

        print("------------------------------------------------------------------------")
        print(f"{'Username':<20} | {'User ID':^10} | {'GSF Android ID'}")
        print("------------------------------------------------------------------------")

        for user_id, username in user_map.items():
            try:
                db_path = f"/data/user/{user_id}/com.google.android.gsf/databases/gservices.db"
                query = f"sqlite3 {db_path} \"select value from main where name = 'android_id';\""
                gsf_id = shell(
                    arg=query,
                    env="ANDROID_RUNTIME_ROOT=/apex/com.android.runtime ANDROID_DATA=/data ANDROID_TZDATA_ROOT=/apex/com.android.tzdata ANDROID_I18N_ROOT=/apex/com.android.i18n"
                ).strip()

                if gsf_id:
                    print(f"{username:<20} | {user_id:^10} | {gsf_id}")
                else:
                    print(f"{username:<20} | {user_id:^10} | (not found)")
            except:
                print(f"{username:<20} | {user_id:^10} | (query error)")

        print("------------------------------------------------------------------------")
        print("   ^----- Open https://google.com/android/uncertified/?pli=1")
        print("          Login with your Google ID, then submit the form with the ID(s) shown above.")

