import os
import shutil
from stuff.general import General
from tools.helper import run
from tools.logger import Logger

class Mitm(General):
    id = "mitm"
    partition = "system"

    def __init__(self, ca_cert_file: str=None) -> None:
        super().__init__()
        self.ca_cert_file = ca_cert_file

    def download(self):
        pass

    def skip_extract(self):
        return True

    def copy(self):
        file_hash = run([
            'openssl', 'x509', '-noout', '-subject_hash_old', '-in',
            self.ca_cert_file,
        ]).stdout.decode("ascii").strip()
        target_dir = os.path.join(
            self.copy_dir, self.partition, "etc", "security", "cacerts")
        Logger.info(f"Creating directory: {target_dir}")
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, f'{file_hash}.0')
        Logger.info(f"Copying {self.ca_cert_file} to system trust store")
        Logger.info(f"Target file: {target_path}")
        shutil.copyfile(self.ca_cert_file, target_path)
        os.chmod(target_path, 0o644)

    def install(self):
        if not self.ca_cert_file:
            raise ValueError(
                "This command requires the --ca-cert switch and a *.pem file")
        super().install()
