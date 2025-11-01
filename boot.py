from network import WLAN, STA_IF
import time
import serve
from creds import SSID, PASSWORD

def connect_wifi(ssid, password,hostname="control"):
    wlan = WLAN(STA_IF)
    wlan.active(True)
    wlan.config(hostname=hostname)
    mac = wlan.config('mac')
    print(':'.join('%02X' % b for b in mac))
    wlan.connect(ssid, password)
    for _ in range(20):
        if wlan.isconnected():
            break
        time.sleep(1)
    print("Connected.", wlan.config("hostname"))
    print("Network config:", wlan.ifconfig())
    return wlan
connect_wifi(SSID, PASSWORD)


serve.serve()
