import os
import platform
import subprocess
import sys
import requests
from tools.logger import Logger
from tqdm import tqdm
import hashlib

def get_download_dir():
    download_loc = ""
    if os.environ.get("XDG_CACHE_HOME", None) is None:
        download_loc = os.path.join('/', "home", os.environ.get("SUDO_USER", os.environ["USER"]), ".cache", "waydroid-script", "downloads")
    else:
        download_loc = os.path.join(os.environ["XDG_CACHE_HOME"], "waydroid-script", "downloads")
    if not os.path.exists(download_loc):
        os.makedirs(download_loc)
    return download_loc

def run(args):
    result = subprocess.run(args=args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # print(result.stdout.decode())
    if result.stderr:
        Logger.error(result.stderr.decode("utf-8"))
        raise subprocess.CalledProcessError(
                    returncode = result.returncode,
                    cmd = result.args,
                    stderr = result.stderr
                )
    return result

def download_file(url, f_name):
    md5 = ""
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    with open(f_name, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    with open(f_name, "rb") as f:
        bytes = f.read()
        md5 = hashlib.md5(bytes).hexdigest()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        raise ValueError("Something went wrong while downloading")
    return md5

def host():
    machine = platform.machine()

    mapping = {
        "i686": ("x86", 32),
        "x86_64": ("x86_64", 64),
        "aarch64": ("arm64-v8a", 64),
        "armv7l": ("armeabi-v7a", 32),
        "armv8l": ("armeabi-v7a", 32)
    }
    if machine in mapping:
        if mapping[machine] == "x86_64":
            with open("/proc/cpuinfo") as f:
                if "sse4_2" not in f.read():
                    Logger.warning("x86_64 CPU does not support SSE4.2, falling back to x86...")
                    return ("x86", 32)
        return mapping[machine]
    raise ValueError("platform.machine '" + machine + "'"
                     " architecture is not supported")


def check_root():
    if os.geteuid() != 0:
        Logger.error("This script must be run as root. Aborting.")
        sys.exit(1)
