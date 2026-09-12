import configparser
from tools.logger import Logger


PROFILES = {
    "pixel6": {
        "ro.product.brand": "google",
        "ro.product.manufacturer": "Google",
        "ro.product.model": "Pixel 6",
        "ro.product.name": "oriole",
        "ro.product.device": "oriole",
        "ro.product.board": "oriole",
        "ro.build.product": "oriole",
        "ro.build.fingerprint": "google/oriole/oriole:13/TQ3A.230901.001/10750268:user/release-keys",
        "ro.build.description": "oriole-user 13 TQ3A.230901.001 10750268 release-keys",
        "ro.build.version.release": "13",
        "ro.build.version.sdk": "33",
        "ro.build.type": "user",
        "ro.build.tags": "release-keys",
    },
    "samsung_s21": {
        "ro.product.brand": "samsung",
        "ro.product.manufacturer": "samsung",
        "ro.product.model": "SM-G991B",
        "ro.product.name": "o1sxeea",
        "ro.product.device": "o1s",
        "ro.product.board": "lahaina",
        "ro.build.product": "o1s",
        "ro.build.fingerprint": "samsung/o1sxeea/o1s:13/TP1A.220624.014/G991BXXU5EWCA:user/release-keys",
        "ro.build.description": "o1sxeea-user 13 TP1A.220624.014 G991BXXU5EWCA release-keys",
        "ro.build.version.release": "13",
        "ro.build.version.sdk": "33",
        "ro.build.type": "user",
        "ro.build.tags": "release-keys",
    },
}

PROP_KEYS = list(next(iter(PROFILES.values())).keys())


class DeviceSpoof:
    id = "device_spoof"

    def __init__(self, profile_name="pixel6") -> None:
        if profile_name not in PROFILES:
            raise ValueError(f"Unknown profile '{profile_name}'. Choose from: {list(PROFILES.keys())}")
        self.profile_name = profile_name
        self.apply_props = PROFILES[profile_name]

    def _read_cfg(self):
        cfg = configparser.ConfigParser()
        cfg.read("/var/lib/waydroid/waydroid.cfg")
        if not cfg.has_section("properties"):
            cfg.add_section("properties")
        return cfg

    def install(self):
        cfg = self._read_cfg()
        for key, value in self.apply_props.items():
            cfg.set("properties", key, value)
        with open("/var/lib/waydroid/waydroid.cfg", "w") as f:
            cfg.write(f)
        Logger.info(f"Device spoofed as '{self.profile_name}'. Restart Waydroid to apply.")

    def uninstall(self):
        cfg = self._read_cfg()
        for key in PROP_KEYS:
            cfg.remove_option("properties", key)
        with open("/var/lib/waydroid/waydroid.cfg", "w") as f:
            cfg.write(f)
        Logger.info("Device spoof properties removed. Restart Waydroid to apply.")
