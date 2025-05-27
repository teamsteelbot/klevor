import asyncio
import io
from multiprocessing import Event
from typing import Awaitable

import websockets
from PIL.Image import Image

from log import Logger

# Server configuration
HOST='localhost'
PORT = 8765

# Serial communication tags
TAG_SERIAL_INCOMING_MESSAGE = "serial_incoming_message"
TAG_SERIAL_OUTGOING_MESSAGE = "serial_outgoing_message"

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
    __log_tag = "RealtimeTrackerServer"
    __host = None
    __port = None
    __connected_clients = None
    __started = None
    __stop_event = None

    def __init__(self, stop_event:Event, logger: Logger, host=HOST, port=PORT):
        """
        Initializes the WebSocket server with the specified host and port.
        """
        # Check the type of stop event
        if not isinstance(stop_event, Event):
            raise ValueError("stop_event must be an instance of Event")
        self.__stop_event = stop_event

        # Check the type of host
        if not isinstance(host, str):
            raise ValueError("host must be a string")
        self.__host = host

        # Check the type of port
        if not isinstance(port, int):
            raise ValueError("port must be an integer")
        self.__port = port

        # Check the type of logger
        if not isinstance(logger, Logger):
            raise ValueError("logger must be an instance of Logger")

        # Get the sub-logger for this class
        self.__logger = logger.get_sub_logger(self.__log_tag)

        # Initialize the connected clients set
        self.__connected_clients = set()

    async def __reactive_handler(self, connection) -> Awaitable[None]:
        """
        Handles WebSocket connections and broadcasts messages to all clients.
        """
        # Add the client to the set of connected clients
        self.__connected_clients.add(connection)
        self.__logger.log(f"Client connected: {connection.remote_address}")

        try:
            while True:
                # Keep the connection alive
                await asyncio.sleep(1)
        except websockets.exceptions.ConnectionClosedOK:
            self.__logger.log(f"Client {connection.remote_address} disconnected gracefully.")
        except websockets.exceptions.ConnectionClosedError as e:
            self.__logger.log(f"Client {connection.remote_address} disconnected with error: {e}")
        except Exception as e:
            self.__logger.log(f"An unexpected error occurred with {connection.remote_address}: {e}")
        finally:
            # Remove the client from the set of connected clients
            self.__connected_clients.remove(connection)
            self.__logger.log(f"Client {connection.remote_address} removed.")

    async def __broadcast_message(self, message):
        """
        Sends a message to all connected clients.
        """
        if self.__connected_clients:  # Only broadcast if there are clients
            await asyncio.gather(*(client.send(message) for client in self.__connected_clients))

    def _send_message(self, message):
        """
        Broadcasts a message to all connected clients.
        """
        asyncio.run_coroutine_threadsafe(self.__broadcast_message(message), asyncio.get_event_loop())

    async def _send_image_with_tag(self, tag: str, img: Image):
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
            self._send_message(tagged_data)
            self.__logger.log(f"Image with tag '{tag}' sent to the clients.")
        except Exception as e:
            self.__logger.log(f"Error sending image: {e}")

    async def send_image_original(self, img: Image):
        """
        Sends the original image to all connected clients.
        """
        await self._send_image_with_tag(TAG_IMAGE_ORIGINAL, img)

    async def send_image_model_g(self, img: Image):
        """
        Sends the image processed by model G to all connected clients.
        """
        await self._send_image_with_tag(TAG_IMAGE_MODEL_G, img)

    async def send_image_model_m(self, img: Image):
        """
        Sends the image processed by model M to all connected clients.
        """
        await self._send_image_with_tag(TAG_IMAGE_MODEL_M, img)

    async def send_image_model_r(self, img: Image):
        """
        Sends the image processed by model R to all connected clients.
        """
        await self._send_image_with_tag(TAG_IMAGE_MODEL_R, img)

    async def send_serial_incoming_message(self, message: str):
        """
        Sends a serial incoming message to all connected clients.
        """
        if not isinstance(message, str):
            raise ValueError("message must be a string")

        # Send a tagged message
        tagged_message = f"{TAG_SERIAL_INCOMING_MESSAGE}:{message}"
        self._send_message(tagged_message)

        # Log
        self.__logger.log(f"Serial incoming message sent: {message}")

    async def send_serial_outgoing_message(self, message: str):
        """
        Sends a serial outgoing message to all connected clients.
        """
        if not isinstance(message, str):
            raise ValueError("message must be a string")

        # Send a tagged message
        tagged_message = f"{TAG_SERIAL_OUTGOING_MESSAGE}:{message}"
        self._send_message(tagged_message)

        # Log
        self.__logger.log(f"Serial outgoing message sent: {message}")

    async def start(self):
        """
        Starts the WebSocket server.
        """
        # Check if it's already running
        if self.__started:
            return

        # Set the started flag
        self.__started = True

        # Start the WebSocket server
        self.__logger.log(f"Starting WebSocket server on ws://{self.__host}:{self.__port}")
        async with websockets.serve(self.__reactive_handler, self.__host, self.__port):
            self.__logger.log("WebSocket server started successfully.")
            self.__stop_event.wait()

        self.__logger.log("WebSocket server is stopping...")
        self.__started = False

async def main(realtime_tracker_server: RealtimeTrackerServer):
    """
    Starts the WebSocket server.
    """
    # Check the type of the realtime tracker server
    if not isinstance(realtime_tracker_server, RealtimeTrackerServer):
        raise ValueError("realtime_tracker_server must be an instance of RealtimeTrackerServer")

    # Start the WebSocket server
    await realtime_tracker_server.start()