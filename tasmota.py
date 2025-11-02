import socket
import tasmota
from ip_addr import PLUG_IPS
def render_page():
    body = "<h2>Local Plug Control</h2><ul>"
    for ip in PLUG_IPS:
        name = tasmota.get_name(ip)
        state = tasmota.get_power_state(ip)
        #color = "green" if state == "ON" else "red"
        if state == "ON":
            next_state = "OFF"
            color = "green"
        elif state == "OFF":
            next_state = "ON"
            color = "red"
        else:  # PENDING or UNKNOWN
            next_state = ""
            color = "orange"
        # Button/link text
        if state == "PENDING":
            action = "<em>Updating...</em>"
        else:
            action = f"<a href='/set?ip={ip}&to={next_state}'>[{next_state}]</a>"

        
        body += (
            "<li>"
            f"<strong>{name}</strong> &nbsp; "
            f"<span style='color:{color}'>{state}</span> &nbsp; "
            f"{action}"
            "</li>"
        )

    body += '</ul><p><a href="/refresh">[Refresh Devices]</a></p>'
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
        if "GET /refresh" in req:
            print("Cache refresh requested")
            tasmota.DEVICE_INFO.clear()  # Wipe all cached data
            cl.send("HTTP/1.1 303 See Other\r\nLocation: /\r\n\r\n")
            cl.close()
            continue
        
        if "GET /set" in req:
            try:
                ip = req.split("ip=")[1].split("&")[0]
                state = req.split("to=")[1].split()[0]
                print("Setting", ip, "to", state)
                tasmota.set_power(ip, state)
            except Exception as e:
                print("Set error:", e)

            cl.send("HTTP/1.1 303 See Other\r\nLocation: /\r\n\r\n")
            cl.close()
            continue



        html = render_page()
        cl.send("HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
        cl.send(html)
        cl.close()


