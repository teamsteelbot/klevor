import asyncio
import io
from typing import Awaitable

import websockets
from PIL.Image import Image

# Server configuration
HOST='localhost'
PORT = 8765

# Image tags
TAG_IMAGE_ORIGINAL = "image_original"
TAG_IMAGE_MODEL_G = "image_model_g"
TAG_IMAGE_MODEL_M = "image_model_m"
TAG_IMAGE_MODEL_R = "image_model_r"

# Image format
IMAGE_FORMAT = "JPEG"

class RealtimeTrackerServer:
    """
    A WebSocket server that handles real-time tracking updates.
    It allows clients to connect and receive messages about tracking events.
    """
    __host = None
    __port = None
    __connected_clients = None
    __started = None

    def __init__(self, host=HOST, port=PORT):
        """
        Initializes the WebSocket server with the specified host and port.
        """
        # Check the type of host and port
        if not isinstance(host, str):
            raise ValueError("host must be a string")

        if not isinstance(port, int):
            raise ValueError("port must be an integer")

        # Set the host, port and initialize the connected clients set
        self.__host = host
        self.__port = port
        self.__connected_clients = set()

    async def __reactive_handler(self, connection) -> Awaitable[None]:
        """
        Handles WebSocket connections and broadcasts messages to all clients.
        """
        # Add the client to the set of connected clients
        self.__connected_clients.add(connection)
        print(f"Client connected: {connection.remote_address}")

        try:
            while True:
                # Keep the connection alive
                await asyncio.sleep(1)
        except websockets.exceptions.ConnectionClosedOK:
            print(f"Client {connection.remote_address} disconnected gracefully.")
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Client {connection.remote_address} disconnected with error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred with {connection.remote_address}: {e}")
        finally:
            # Remove the client from the set of connected clients
            self.__connected_clients.remove(connection)
            print(f"Client {connection.remote_address} removed.")

    async def __broadcast_message(self, message):
        """
        Sends a message to all connected clients.
        """
        if self.__connected_clients:  # Only broadcast if there are clients
            await asyncio.gather(*(client.send(message) for client in self.__connected_clients))

    def send_message(self, message):
        """
        Broadcasts a message to all connected clients.
        """
        asyncio.run_coroutine_threadsafe(self.__broadcast_message(message), asyncio.get_event_loop())

    async def send_image_with_tag(self, tag: str, img: Image):
        """
        Sends an image with a tag to all the connected clients.
        """
        try:
            # Open the image and convert it to a binary stream
            img_stream = io.BytesIO()
            img.save(img_stream, format=IMAGE_FORMAT)
            img_stream.seek(0)
            binary_data = img_stream.read()

            # Prepend the tag to the binary data
            tagged_data = f"{tag}:".encode() + binary_data

            # Send the tagged binary data to the clients
            self.send_message(tagged_data)
            print(f"Image with tag '{tag}' sent to the clients.")
        except Exception as e:
            print(f"Error sending image: {e}")

    async def start(self):
        """
        Starts the WebSocket server.
        """
        # Check if it's already running
        if self.__started:
            print("WebSocket server is already running.")
            return

        # Set the started flag
        self.__started = True

        print(f"Starting WebSocket server on ws://{HOST}:{PORT}")
        async with websockets.serve(self.__reactive_handler, HOST, PORT):
            await asyncio.Future()  # Run forever

async def main(realtime_tracker_server: RealtimeTrackerServer):
    """
    Starts the WebSocket server.
    """
    # Check the type of the realtime tracker server
    if not isinstance(realtime_tracker_server, RealtimeTrackerServer):
        raise ValueError("realtime_tracker_server must be an instance of RealtimeTrackerServer")

    # Start the WebSocket server
    await realtime_tracker_server.start()