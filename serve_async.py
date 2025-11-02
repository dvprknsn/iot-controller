# serve_async_safe.py
import uasyncio as asyncio
import tasmota
from ip_addr import PLUG_IPS

def render_page():
    body = "<h2>Local Plug Control</h2><ul>"
    for ip in PLUG_IPS:
        name = tasmota.get_name(ip)
        state = tasmota.get_power_state(ip)

        if state == "ON":
            next_state = "OFF"
            color = "green"
        elif state == "OFF":
            next_state = "ON"
            color = "red"
        else:
            next_state = ""
            color = "gray"

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
    page = f"""\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>ESP Plug Control</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta http-equiv="refresh" content="5">
</head>
<body>{body}</body>
</html>"""
    headers = "HTTP/1.0 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n"
    return (headers + page).encode("utf-8")

async def poll_pending():
    while True:
        for ip, info in list(tasmota.DEVICE_INFO.items()):
            if info.get("pending", False):
                # Query actual state
                tasmota.get_power_state(ip)
        await asyncio.sleep(1)

async def serve_client(reader, writer):
    try:
        req = await reader.read(1024)
        if not req:
            writer.close()
            await asyncio.sleep(0)
            return

        req = req.decode("utf-8", "ignore")

        if "GET /refresh" in req:
            tasmota.DEVICE_INFO.clear()
            writer.write(b"HTTP/1.1 303 See Other\r\nLocation: /\r\n\r\n")
            await writer.drain()
            writer.close()
            await asyncio.sleep(0)
            return

        if "GET /set" in req:
            try:
                ip = req.split("ip=")[1].split("&")[0]
                state = req.split("to=")[1].split()[0]
                tasmota.set_power(ip, state)
            except Exception as e:
                print("Set error:", e)

            writer.write(b"HTTP/1.1 303 See Other\r\nLocation: /\r\n\r\n")
            await writer.drain()
            writer.close()
            await asyncio.sleep(0)
            return

        page = render_page()
        writer.write(page)
        await writer.drain()
        writer.close()
        await asyncio.sleep(0)

    except Exception as exc:
        print("serve_client error:", exc)
        writer.close()
        await asyncio.sleep(0)


async def main():
    server = await asyncio.start_server(serve_client, "0.0.0.0", 80)
    print("Async Server running on port 80")
    asyncio.create_task(poll_pending())
    while True:
        await asyncio.sleep(3600)
        


asyncio.run(main())

