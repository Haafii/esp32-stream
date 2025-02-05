import asyncio
import websockets

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket!")
            await websocket.send("test_frame_data")  # Simulating a frame
            print("Frame sent!")
    except Exception as e:
        print("WebSocket connection failed:", e)

asyncio.run(test_websocket())
