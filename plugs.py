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

