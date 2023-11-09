import hashlib
import platform
import subprocess

from omegaconf import OmegaConf


class HWIDVerify:
    def __init__(self):
        pass

    def get_windows_hwid(self):
        cmd = "wmic csproduct get UUID"
        result = subprocess.getoutput(cmd)
        uuid = result.split("\n")[2].strip()
        return uuid

    def get_linux_hwid(self):
        cpu_serial = subprocess.getoutput(
            "cat /proc/cpuinfo | grep 'serial' | awk '{print $3}'"
        ).strip()
        motherboard_serial = subprocess.getoutput(
            "dmidecode -t baseboard | grep 'Serial Number' | awk '{print $3}'"
        ).strip()
        mac_address = subprocess.getoutput(
            "cat /sys/class/net/$(ip route show default | awk '/default/ {print $5}')/address"
        ).strip()
        hw_info = cpu_serial + motherboard_serial + mac_address
        hwid = hashlib.sha256(hw_info.encode()).hexdigest()
        return hwid

    def get_hwid(self):
        current_platform = platform.system().lower()
        if current_platform == "windows":
            return self.get_windows_hwid()
        elif current_platform == "linux":
            return self.get_linux_hwid()
        else:
            raise Exception("Unsupported platform: " + current_platform)

    def add_hwid_to_whitelist(self, hwid, file_path="whitelist.yaml"):
        config = OmegaConf.load(file_path)
        if hwid not in config.allowed_api:
            config.allowed_api.append(hwid)
            with open(file_path, "w") as f:
                OmegaConf.save(config, f)
            print(f"HWID {hwid} added to whitelist.")
        else:
            print(f"HWID {hwid} already in whitelist.")


hwid = HWIDVerify().get_hwid()
HWIDVerify().add_hwid_to_whitelist(hwid)
