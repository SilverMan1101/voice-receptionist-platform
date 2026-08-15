import websocket

url = "wss://marina-poncho-avenging.ngrok-free.dev/internal/telephony/stream"

print("Connecting to:", url)

try:
    ws = websocket.create_connection(
        url,
        timeout=10
    )

    print("CONNECTED!")

    ws.send("hello")

    message = ws.recv()
    print("Received:", message)

    ws.close()

except Exception as e:
    print("WEBSOCKET ERROR:")
    print(repr(e))