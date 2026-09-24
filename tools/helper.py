import gzip
import os
import re
import platform
import subprocess
import sys
import requests
from tools.logger import Logger
from tqdm import tqdm
import hashlib
from typing import Optional

def get_download_dir():
    if os.environ.get("XDG_CACHE_HOME"):
        download_loc = os.path.join(
            os.environ["XDG_CACHE_HOME"], "waydroid-script", "downloads"
        )
    else:
        user = os.environ.get("SUDO_USER", os.environ.get("USER", "root"))
        download_loc = os.path.join("/", "home", user, ".cache", "waydroid-script", "downloads")
        
    if not os.path.exists(download_loc):
        os.makedirs(download_loc, exist_ok=True)
    return download_loc

def get_data_dir():
    user = os.environ.get("SUDO_USER", os.environ.get("USER", "root"))
    return os.path.join("/", "home", user, ".local", "share", "waydroid", "data")

def run(args: list, env: Optional[dict] = None, ignore: Optional[str] = None):
    result = subprocess.run(
        args=args, 
        env=env, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )

    if result.stderr:
        error = result.stderr.decode("utf-8").strip()
        
        if (ignore and re.search(ignore, error)) or "system_ota" in error:
            return result
        
        Logger.error(error)
        raise subprocess.CalledProcessError(
            returncode=result.returncode,
            cmd=result.args,
            stderr=result.stderr
        )
    return result

def shell(arg: str, env: Optional[str] = None):
    cmd = ["sudo", "waydroid", "shell"]
    process = subprocess.Popen(
        args=cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    boot_classpath = "export BOOTCLASSPATH=/apex/com.android.art/javalib/core-oj.jar:/apex/com.android.art/javalib/core-libart.jar:/apex/com.android.art/javalib/core-icu4j.jar:/apex/com.android.art/javalib/okhttp.jar:/apex/com.android.art/javalib/bouncycastle.jar:/apex/com.android.art/javalib/apache-xml.jar:/system/framework/framework.jar:/system/framework/ext.jar:/system/framework/telephony-common.jar:/system/framework/voip-common.jar:/system/framework/ims-common.jar:/system/framework/framework-atb-backward-compatibility.jar:/apex/com.android.conscrypt/javalib/conscrypt.jar:/apex/com.android.media/javalib/updatable-media.jar:/apex/com.android.mediaprovider/javalib/framework-mediaprovider.jar:/apex/com.android.os.statsd/javalib/framework-statsd.jar:/apex/com.android.permission/javalib/framework-permission.jar:/apex/com.android.sdkext/javalib/framework-sdkextensions.jar:/apex/com.android.wifi/javalib/framework-wifi.jar:/apex/com.android.tethering/javalib/framework-tethering.jar"
    
    full_script = f"{boot_classpath}\n"
    if env:
        full_script += f"{env}\n"
    full_script += f"{arg}\n"

    stdout, stderr = process.communicate(input=full_script)

    if process.returncode != 0 and stderr:
        Logger.error(stderr.strip())
        raise subprocess.CalledProcessError(
            returncode=process.returncode,
            cmd=cmd,
            stderr=stderr.encode()
        )
    return stdout

def download_file(url, f_name):
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024 
    
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    with open(f_name, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()

    hash_md5 = hashlib.md5()
    with open(f_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        raise ValueError("Download incomplete or corrupted")
    
    return hash_md5.hexdigest()

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
        if machine == "x86_64":
            try:
                with open("/proc/cpuinfo", "r") as f:
                    if "sse4_2" not in f.read():
                        Logger.warning("CPU does not support SSE4.2, falling back to x86...")
                        return ("x86", 32)
            except Exception:
                pass
        return mapping[machine]
    
    raise ValueError(f"Architecture '{machine}' is not supported")

def check_root():
    if os.geteuid() != 0:
        Logger.error("This script must be run as root (sudo). Aborting.")
        sys.exit(1)

def backup(path):
    if not os.path.exists(path):
        return
    gz_filename = path + ".gz"
    with open(path, "rb") as f_in:
        with gzip.open(gz_filename, "wb") as f_out:
            f_out.writelines(f_in)

def restore(path):
    gz_filename = path + ".gz"
    if not os.path.exists(gz_filename):
        return
    with gzip.open(gz_filename, "rb") as f_in:
        with open(path, "wb") as f_out:
            f_out.write(f_in.read())