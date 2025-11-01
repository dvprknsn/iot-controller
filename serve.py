import socket
import plugs

def render_page():
    rows = []
    for name in plugs.PLUGS:
        state = plugs.get_state(name)
        label = f"{name.upper()} ({state})"
        rows.append(
            f'<p>{label} '
            f'<a href="/do?plug={name}&action=toggle">'
            f'<button>Toggle</button></a></p>'
        )
    return (
        "<!DOCTYPE html><html><head><title>Control</title></head><body>"
        "<h1>Plug Control</h1>" +
        "".join(rows) +
        "</body></html>"
    )

def serve():
    s = socket.socket()
    s.bind(('', 80))
    s.listen(5)
    print("Server started on port 80...")

    while True:
        cl, addr = s.accept()
        request = cl.recv(1024).decode()
        print("Request:", request)

        if "GET /do?" in request:
            try:
                path = request.split(" ")[1]
                params = path.split("?")[1]
                pairs = dict(p.split("=") for p in params.split("&"))
                plug = pairs.get("plug")
                action = pairs.get("action")

                if action == "toggle":
                    plugs.toggle(plug)

                cl.send("HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n")

            except Exception as e:
                print("Error:", e)
                cl.send("HTTP/1.1 500 Internal Error\r\n\r\n")

        else:
            html = render_page()
            cl.send('HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(html)

        cl.close()

