#tasmota.py
import requests
import ujson
import re
DEVICE_INFO = {}
# Cache: ip -> {"name": str, "state": str}
def get_name(ip):
    """Return cached or freshly retrieved Tasmota DeviceName."""
    if ip in DEVICE_INFO and "name" in DEVICE_INFO[ip]:
        return DEVICE_INFO[ip]["name"]
    try:
        url = "http://%s/cm?cmnd=DeviceName" % ip
        r = requests.get(url, timeout=2)
        text = r.text
        r.close()
        # Try to parse JSON normally first
        try:
            data = ujson.loads(text)
            name = data.get("DeviceName", ip)
        except:
            # If JSON parsing fails, extract DeviceName manually
            match = re.search(r'"DeviceName":"([^"]+)"', text)
            name = match.group(1) if match else "Unknown (%s)" % ip
    except: name = "Unknown (%s)" % ip
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
        # Extract POWER value directly
        match = re.search(r'"POWER":"(ON|OFF)"', text)
        state = match.group(1) if match else "UNKNOWN"
    except:
        state = "UNKNOWN"
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


#def toggle(ip):
#    """Toggle power state."""
#     url = "http://%s/cm?cmnd=Power%%20TOGGLE" % ip
#     try:
#         r = requests.get(url, timeout=2)
#         r.close()
#         return True
#     except: return False
