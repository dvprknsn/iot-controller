#plugs.py
import urequests as requests

PLUGS = {
    "one": "192.168.68.91",
    "two": "192.168.68.92"
}

def toggle(name):
    if name not in PLUGS:
        raise ValueError("Unknown plug")
    ip = PLUGS[name]
    url = f"http://{ip}/cm?cmnd=Power%20TOGGLE"
    resp = requests.get(url)
    resp.close()
    
def get_state(name):
    ip = PLUGS.get(name)
    if not ip:
        return "UNKNOWN"
    try:
        url = f"http://{ip}/cm?cmnd=Power"
        resp = requests.get(url)
        data = resp.json()
        resp.close()
        return data.get("POWER", "UNKNOWN")
    except Exception:
        return "UNKNOWN"


