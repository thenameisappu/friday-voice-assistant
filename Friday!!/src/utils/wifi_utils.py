import subprocess
import re
import time

def get_current_ssid():
    result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True)
    output = result.stdout
    match = re.search(r"^\s*SSID\s*:\s(.+)$", output, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def list_wifi_networks():
    result = subprocess.run(["netsh", "wlan", "show", "networks"], capture_output=True, text=True)
    return re.findall(r"SSID \d+ : (.+)", result.stdout)

def create_wifi_profile(ssid, password):
    profile = f"""
    <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
        <name>{ssid}</name>
        <SSIDConfig>
            <SSID>
                <name>{ssid}</name>
            </SSID>
        </SSIDConfig>
        <connectionType>ESS</connectionType>
        <connectionMode>manual</connectionMode>
        <MSM>
            <security>
                <authEncryption>
                    <authentication>WPA2PSK</authentication>
                    <encryption>AES</encryption>
                    <useOneX>false</useOneX>
                </authEncryption>
                <sharedKey>
                    <keyType>passPhrase</keyType>
                    <protected>false</protected>
                    <keyMaterial>{password}</keyMaterial>
                </sharedKey>
            </security>
        </MSM>
    </WLANProfile>
    """
    with open("wifi_profile.xml", "w") as f:
        f.write(profile)

def is_connected_to(ssid, timeout=15):
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_ssid = get_current_ssid()
        if current_ssid == ssid:
            result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True)
            if re.search(r"^\s*State\s*:\s*connected\s*$", result.stdout, re.IGNORECASE | re.MULTILINE):
                return True
        time.sleep(1)
    return False

def connect_to_wifi(ssid, password):
    create_wifi_profile(ssid, password)
    subprocess.run(["netsh", "wlan", "add", "profile", "filename=wifi_profile.xml"], capture_output=True)
    subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"], capture_output=True)
    return is_connected_to(ssid)
