#tasmota.py
import requests

DEVICE_INFO = {}  # Cache: ip -> {"name": str, "state": str}

def fetch_status(ip):
    """Retrieve full Tasmota status JSON (Status0)."""
    try:
        url = "http://%s/cm?cmnd=Status%%200" % ip
        r = requests.get(url)
        data = r.json()
        r.close()
        return data
    except:
        return None


def get_name(ip):
    """Return cached or freshly retrieved Tasmota DeviceName."""
    if ip in DEVICE_INFO and "name" in DEVICE_INFO[ip]:
        return DEVICE_INFO[ip]["name"]

    data = fetch_status(ip)
    if not data:
        name = "Unknown (%s)" % ip
    else:
        name = data.get("Status", {}).get("DeviceName", ip)

    DEVICE_INFO.setdefault(ip, {})["name"] = name
    return name


def get_power_state(ip):
    """Return ON, OFF, or UNKNOWN"""
    try:
        url = "http://%s/cm?cmnd=Power" % ip
        r = requests.get(url)
        data = r.json()
        r.close()
        state = data.get("POWER", "UNKNOWN")
    except:
        state = "UNKNOWN"

    DEVICE_INFO.setdefault(ip, {})["state"] = state
    return state


def toggle(ip):
    """Toggle power state."""
    url = "http://%s/cm?cmnd=Power%%20TOGGLE" % ip
    try:
        r = requests.get(url)
        r.close()
        return True
    except:
        return False

