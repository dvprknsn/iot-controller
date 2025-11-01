import socket
import tasmota

# IPs of Tasmota devices
PLUG_IPS = [
    "192.168.68.91",
    "192.168.68.92"
]

def render_page():
    body = "<h2>Local Plug Control</h2><ul>"

    for ip in PLUG_IPS:
        name = tasmota.get_name(ip)
        state = tasmota.get_power_state(ip)
        color = "green" if state == "ON" else "red"

        body += (
            "<li>"
            f"<strong>{name}</strong> &nbsp; "
            f"<span style='color:{color}'>{state}</span> &nbsp; "
            f"<a href='/toggle?ip={ip}'>[Toggle]</a>"
            "</li>"
        )

    body += "</ul>"
    return f"""\
<!DOCTYPE html>
<html>
<head>
<title>ESP Plug Control</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body>{body}</body>
</html>"""


def serve(port=80):
    addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(2)
    print("Server running at :", addr)

    while True:
        cl, addr = s.accept()
        req = cl.recv(1024).decode()
        print("Request from", addr)
        print(req)

        if "GET /toggle" in req:
            try:
                ip = req.split("ip=")[1].split()[0]
                print("Toggle request for", ip)
                tasmota.toggle(ip)
            except Exception as e:
                print("Toggle error:", e)

        
            cl.send("HTTP/1.1 303 See Other\r\nLocation: /\r\n\r\n")
            cl.close()
            continue

        html = render_page()
        cl.send("HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
        cl.send(html)
        cl.close()

