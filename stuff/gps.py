import os
from xml.dom import minidom
import xml.etree.ElementTree as ET
import shutil
from stuff.general import General
from tools.logger import Logger
import tools.images as images
from tools.helper import run, host 
from tools import container

class GPS(General):
    id = "gps"
    partition = "vendor"
    dl_links = ["https://github.com/Lolmc0587/android_gps_libraries/archive/refs/tags/2.1.zip","f84c369c7cebd9dbb8987ca15c6aa856"]
    act_md5 = ...
    dl_link = ...
    dl_file_name = "android_gps_libraries-2.1.zip"
    extract_to = "/tmp/android_gps_libraries-2.1"

    files = [
        "lib/hw/android.hardware.gnss@1.0-impl.so",
        "lib64/hw/android.hardware.gnss@1.0-impl.so",
        "lib/hw/gps.default.so",
        "lib64/hw/gps.default.so",
        "etc/init/android.hardware.gnss@1.0-service.rc",
    ]
    

    def __init__(self, android_version="11", gps_host="/dev/ttyGPSD", baud_rate=9600) -> None:
        super().__init__()
        self.host_arch = host()
        # Set for arm 32 bit support from file downloaded 
        self.host = "arm64-v8a" if "arm" in self.host_arch[0] else self.host_arch[0]
        self.gps_host = gps_host
        self.baud_rate = baud_rate
        self.android_version = android_version
        self.usb_name = self.gps_host.split("/")[-1]
        self.files_vendor = [
            "bin/hw/android.hardware.gnss@1.0-service",
        ]
        self.config_files = {
            "11": [
                "etc/vintf/compatibility_matrix.legacy.xml",
                "etc/vintf/manifest.xml",
                "build.prop",
            ],
            "13": [
                "etc/vintf/compatibility_matrix.7.xml",
                "etc/vintf/manifest.xml",
                "build.prop",
            ],
        }
    
        self.compatibility_files = {
            "11": "etc/vintf/compatibility_matrix.legacy.xml",
            "13": "etc/vintf/compatibility_matrix.7.xml",
        }

        self.dl_link = self.dl_links[0]
        self.act_md5 = self.dl_links[1]

    def update_manifest(self, manifest_path, data):
        """
        Update the manifest file by inserting data into the <manifest> tag and format the XML.
        """
        tree = ET.parse(manifest_path)
        root = tree.getroot()

        root.append(ET.fromstring(data))
        tree.write(manifest_path, encoding="utf-8", xml_declaration=True)

        with open(manifest_path, "r") as f:
            content = f.read()
            formatted_content = minidom.parseString(content).toprettyxml(indent="    ")

        formatted_content = "\n".join(
            [line for line in formatted_content.split("\n") if line.strip()]
        )

        with open(manifest_path, "w") as f:
            f.write(formatted_content)

    def copy(self):
        Logger.info("Copying gps library files ...")
        if self.android_version == "11":
            shutil.copytree(os.path.join(self.extract_to, self.dl_file_name.replace(".zip", ""), self.android_version,
                        self.host, "system"), os.path.join(self.copy_dir, "system"), dirs_exist_ok=True)
            self.partition = "system"
        if self.android_version == "13":
            shutil.copytree(os.path.join(self.extract_to, self.dl_file_name.replace(".zip", ""), self.android_version,
                            self.host, "system"), os.path.join(self.copy_dir, "vendor"), dirs_exist_ok=True)
            self.partition = "vendor"
        shutil.copytree(os.path.join(self.extract_to, self.dl_file_name.replace(".zip", ""), self.android_version,
                        self.host, "vendor"), os.path.join(self.copy_dir, "vendor"), dirs_exist_ok=True)
        
    def extra1(self):
        Logger.info("Setting extra permissions ...")
        # set permissions for vendor files
        path = os.path.join(self.copy_dir, "vendor", self.files_vendor[0])
        self.set_perm2(path, recursive=True)
        
        # Copy nessessary files to the overlayfs
        container.stop()
        copy_dir = "/tmp/waydroid"
        if container.use_overlayfs():
            img = os.path.join(images.get_image_dir(), "system.img")
            # images.mount(img, copy_dir)
            if not os.path.exists(copy_dir):
                os.makedirs(copy_dir)
            run(["sudo", "mount", img, copy_dir])

            for file in self.config_files[self.android_version]:
                file_dir = os.path.join(self.copy_dir, "system", file)
                if not os.path.exists(os.path.dirname(file_dir)):
                    os.makedirs(os.path.dirname(file_dir))
                shutil.copyfile(os.path.join(copy_dir, "system", file), file_dir)
                self.set_perm2(file_dir, recursive=True)

            if self.android_version == "13":
                # Copy missing libraries file for android 13 vendor partition from system partition
                if not os.path.exists(os.path.join(self.copy_dir, "vendor", "lib64", "hw")):
                    os.makedirs(os.path.join(self.copy_dir, "vendor", "lib64", "hw"))

                copy_ = True
                if "arm" in self.host and self.host_arch[1] == 32:
                    copy_ = False
                if copy_:
                    shutil.copyfile(os.path.join(copy_dir, "system", "lib64/android.hardware.gnss@1.0.so"),
                                    os.path.join(self.copy_dir, "vendor", "lib64/hw/android.hardware.gnss@1.0.so"))
                
                if not os.path.exists(os.path.join(self.copy_dir, "vendor", "lib", "hw")):
                    os.makedirs(os.path.join(self.copy_dir, "vendor", "lib", "hw"))

                shutil.copyfile(os.path.join(copy_dir, "system", "lib/android.hardware.gnss@1.0.so"),
                                os.path.join(self.copy_dir, "vendor", "lib/hw/android.hardware.gnss@1.0.so"))
                
            images.umount(copy_dir)
        
        # Update manifest files
        container.upgrade()
        
        manifest_entry_1 = """
            <hal format="hidl" optional="true">
                <name>android.hardware.gnss</name>
                <version>1.0</version>
                <interface>
                    <name>IGnss</name>
                    <instance>default</instance>
                </interface>
            </hal>
        """
        self.update_manifest(
            os.path.join(self.copy_dir, "system", self.compatibility_files[self.android_version]),
            data=manifest_entry_1,
        )

        manifest_entry_2 = """
            <hal format="hidl">
                <name>android.hardware.gnss</name>
                <transport>hwbinder</transport>
                <version>1.0</version>
                <interface>
                    <name>IGnss</name>
                    <instance>default</instance>
                </interface>
                <fqname>@1.0::IGnss/default</fqname>
            </hal>
        """
        self.update_manifest(os.path.join(self.copy_dir, "system", "etc", "vintf", "manifest.xml"), data=manifest_entry_2)
        config_nodes = "/var/lib/waydroid/lxc/waydroid/config_nodes"
        # lxc.mount.entry = /dev/ttyGPSD dev/ttyGPSD none bind,create=file,optional 0 0

        with open(config_nodes, "a") as f:
            f.write(f"lxc.mount.entry = {self.gps_host} dev/{self.usb_name} none bind,create=file,optional 0 0\n")

        with open(os.path.join(self.copy_dir, "system", "build.prop"), "a") as f:
            f.write("ro.factory.hasGPS=true\n")
            f.write(f"ro.kernel.android.gps={self.usb_name}\n")
            f.write(f"ro.kernel.android.gps.speed={self.baud_rate}\n")
        Logger.warning(
            "You need to add user to the 'dialout' group to access the GPS device."
            "\nYou can do this by running: sudo usermod -aG dialout <your_username>"
            "\nand then reboot your system."
        )
    def extra2(self):
        # Remove vendor files from system partition
        self.files = self.files_vendor
        self.partition = "vendor"
        self.remove()

        # Remove config files from system partition
        self.files = self.config_files[self.android_version]
        self.partition = "system"
        self.remove()

        container.upgrade()
        
