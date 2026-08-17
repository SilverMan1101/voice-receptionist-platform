import asyncio
import websockets
import json


async def test():
    url = "wss://marina-poncho-avenging.ngrok-free.dev/internal/telephony/stream"

    print("Connecting to:", url)

    async with websockets.connect(url) as websocket:
        print("WEBSOCKET CONNECTED!")

        await websocket.send(json.dumps({
            "event": "connected",
            "protocol": "Call",
            "version": "1.0"
        }))

        await websocket.send(json.dumps({
            "event": "start",
            "start": {
                "callSid": "TEST_CALL",
                "streamSid": "TEST_STREAM",
                "tracks": ["inbound"],
                "mediaFormat": {
                    "encoding": "audio/x-mulaw",
                    "sampleRate": 8000,
                    "channels": 1
                },
                "customParameters": {
                    "test": "voice-receptionist"
                }
            }
        }))

        await asyncio.sleep(2)

        print("Closing...")


asyncio.run(test())