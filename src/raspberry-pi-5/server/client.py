from websockets import connect
import asyncio

from server import RealtimeTrackerServer
 
async def ws_client():
    """
    WebSocket client that connects to the server and sends user input.
    This client will send the user's name and age to the server
    and listen for incoming messages indefinitely.
    """
    # Connect to the server
    url = f'ws://{RealtimeTrackerServer.HOST}:{RealtimeTrackerServer.PORT}'
    print(f"Connecting to WebSocket server at {url}...")
    async with connect(url) as ws: 
        # Stay alive forever, listen to incoming msgs
        while True:
            msg = await ws.recv()
            print(msg)

if __name__ == "__main__":
    # Start the connection
    asyncio.run(ws_client())
