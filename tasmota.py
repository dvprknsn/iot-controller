# tasmota.py
import requests
import ujson
import re

DEVICE_INFO = {}  # Cache: ip -> {"name": str, "state": str, "pending": bool}

def get_name(ip):
    if ip in DEVICE_INFO and "name" in DEVICE_INFO[ip]:
        return DEVICE_INFO[ip]["name"]
    try:
        url = "http://%s/cm?cmnd=DeviceName" % ip
        r = requests.get(url, timeout=2)
        data = ujson.loads(r.text)
        r.close()
        name = data.get("DeviceName", ip)
    except:
        name = "Unknown (%s)" % ip
    
    DEVICE_INFO.setdefault(ip, {})["name"] = name
    return name


def get_power_state(ip):
    """Return ON, OFF, or PENDING"""
    pending = DEVICE_INFO.get(ip, {}).get("pending", False)

    try:
        url = "http://%s/cm?cmnd=Power" % ip
        r = requests.get(url, timeout=2)
        text = r.text
        r.close()
        match = re.search(r'"POWER":"(ON|OFF)"', text)
        state = match.group(1) if match else "UNKNOWN"
    except:
        state = "UNKNOWN"

    # If we previously sent a change and it now matches real state → clear pending
    if pending and state in ("ON", "OFF"):
        DEVICE_INFO[ip]["pending"] = False

    DEVICE_INFO.setdefault(ip, {})["state"] = state
    return "PENDING" if pending else state


def set_power(ip, state):
    """State: ON or OFF"""
    url = "http://%s/cm?cmnd=Power%%20%s" % (ip, state)
    try:
        r = requests.get(url, timeout=2)
        r.close()
        DEVICE_INFO.setdefault(ip, {})["pending"] = True
        return True
    except:
        return False
