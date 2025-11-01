#tasmota.py
import requests
import ujson

DEVICE_INFO = {}  # Cache: ip -> {"name": str, "state": str}

def fetch_status(ip):
    """Retrieve full Tasmota status JSON (Status0)."""
    try:
        url = "http://%s/cm?cmnd=Status%%200" % ip
        r = requests.get(url)
        text = r.text
        r.close()
        
        # Try to parse JSON normally first
        try:
            import ujson
            data = ujson.loads(text)
            return data
        except:
            # If JSON parsing fails, extract DeviceName manually
            import re
            match = re.search(r'"DeviceName":"([^"]+)"', text)
            if match:
                return {"Status": {"DeviceName": match.group(1)}}
            return None
    except Exception as e:
        print("Exception:", type(e).__name__, str(e))
        return None


def get_name(ip):
    """Return cached or freshly retrieved Tasmota DeviceName."""
    if ip in DEVICE_INFO and "name" in DEVICE_INFO[ip]:
        return DEVICE_INFO[ip]["name"]
    data = fetch_status(ip)
    print("Fetched data:", data)  # Debug line
    if not data:
        name = "Unknown (%s)" % ip
    else:
        status_obj = data.get("Status", {})
        print("Status object:", status_obj)  # Debug line
        device_name = status_obj.get("DeviceName", ip)
        print("DeviceName:", device_name)  # Debug line
        name = device_name
    DEVICE_INFO.setdefault(ip, {})["name"] = name
    return name

def get_power_state(ip):
    """Return ON, OFF, or UNKNOWN"""
    try:
        url = "http://%s/cm?cmnd=Power" % ip
        r = requests.get(url)
        text = r.text
        r.close()
        
        # Extract POWER value directly
        import re
        match = re.search(r'"POWER":"(ON|OFF)"', text)
        state = match.group(1) if match else "UNKNOWN"
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

