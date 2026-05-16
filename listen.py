import asyncio
import websockets

async def listen_for_alerts():
    uri = "ws://localhost:8000/ws/alerts"
    try:
        async with websockets.connect(uri) as websocket:
            print("🟢 Connected! Listening for live hospital alerts...")
            while True:
                # Wait for a message to be broadcasted
                message = await websocket.recv()
                print(f"\n🚨 INCOMING ALERT: {message}\n")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(listen_for_alerts())