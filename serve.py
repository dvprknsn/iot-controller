import socket
import plugs

HTML = """
<!DOCTYPE html>
<html>
<head><title>Control</title></head>
<body>
<h1>Plug Control</h1>
<a href="/do?plug=one&action=toggle">
    <button>Toggle PLUG ONE</button>
</a>
<a href="/do?plug=two&action=toggle">
    <button>Toggle PLUG TWO</button>
</a>
</body></html>
"""

def serve():
    s = socket.socket()
    s.bind(('', 80))
    s.listen(5)
    print("Server started on port 80...")

    while True:
        cl, addr = s.accept()
        request = cl.recv(1024).decode()
        print("Request:", request)

        # Parse route
        if "GET /do?" in request:
            try:
                # Naive parameter parsing:
                path = request.split(" ")[1]
                params = path.split("?")[1]
                pairs = dict(p.split("=") for p in params.split("&"))
                plug = pairs.get("plug")
                action = pairs.get("action")

                if action == "toggle":
                    plugs.toggle(plug)

                # Redirect to the safe main page:
                cl.send("HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n")
            except Exception as e:
                print("Error:", e)
                cl.send("HTTP/1.1 500 Internal Error\r\n\r\n")

        else:
            cl.send('HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(HTML)

        cl.close()
