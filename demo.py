import base64
import hashlib
import json
import platform
import subprocess

import requests


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


class CaptchaResolver:
    def __init__(self):
        pass

    def get_captcha_code(self, image_input):
        url = "http://csgo.mai0313.com:7777/get_captcha_code"

        payload = {"captcha_base64": image_input}

        headers = {"Content-Type": "application/json", "X-API-Key": HWIDVerify().get_hwid()}

        response = requests.post(url, data=json.dumps(payload), headers=headers)

        if response.status_code == 200:
            return response.json().get("result")
        elif response.status_code == 403:
            print(f"{response.json().get('result')}: {response.json().get('message')}")
        else:
            print("調用API出錯 狀態碼:", response.status_code)

    def image_to_base64(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")


if __name__ == "__main__":
    image_path = "data/test.jpg"
    image_path = CaptchaResolver().image_to_base64(image_path)
    result = CaptchaResolver().get_captcha_code(image_path)
    print(result)
    if result:
        print("解析的驗證碼是:", result)
