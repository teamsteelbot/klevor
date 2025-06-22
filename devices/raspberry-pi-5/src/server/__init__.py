import asyncio
import io
from threading import Thread
from multiprocessing import Event, RLock
from typing import Optional, final

from websockets import serve, exceptions
from PIL.Image import Image

from .constants import  HOST, PORT
from ..camera.constants import IMAGE_FORMAT
from .abstracts import WebsocketsServerABC
from ..log import LoggerABC
from ..log.sub_logger import SubLogger
from ..utils import is_instance, get_local_ip
from .message import Message
from .enums import Tag
from ..constants import MODEL_G, MODEL_M, MODEL_R

class WebsocketsServer(WebsocketsServerABC):
    """
    Class for a WebSocket server that handles real-time tracking updates.
    It allows clients to connect and receive messages about tracking events.

    This is only used on practices, not in the competition, to test new features and models in real-time.
    """

    # Logger configuration
    LOG_TAG = "WebsocketServer"

    def __init__(
        self,
        logger: Optional[LoggerABC] = None,
        host: str = HOST,
        port: int = PORT
    ):
        """
        Initializes the WebSocket server with the specified host and port.

        Args:
            logger (Optional[LoggerABC]): Logger instance for logging messages.
            host (str): The host address for the WebSocket server. Default is 'localhost'.
            port (int): The port number for the WebSocket server. Default is 8765.
        """
        # Create a reentrant lock
        self.__rlock = RLock()
        
        # Create a stop event
        self.__stop_event = Event()
        self.__stop_event.set()

        # Create the parking event
        self.__parking_event = Event()

        # Check the type of logger
        is_instance(logger, LoggerABC) if logger else None

        # Get the sub-logger for this class
        self.__logger = SubLogger(logger, self.LOG_TAG) if logger else None

        # Check the type of host
        is_instance(host, str)
        self.__host = host

        # Check the type of port
        is_instance(port, int)
        self.__port = port

        # Initialize the connected clients set
        self.__connected_clients = set()

        # Initialize the thread
        self.__thread = None

    async def __reactive_handler(self, connection) -> None:
        """
        Handles WebSocket connections and broadcasts messages to all clients.
        """
        # Add the client to the set of connected clients
        self.__connected_clients.add(connection)
        self.__logger.debug(f"Client connected: {connection.remote_address}") if self.__logger else None

        # Send a welcome message immediately upon connection
        await self._send_message(connection, Message(Tag.CONNECTION_STATUS, "Connected to WebsocketServer"))

        try:
            while not self.__stop_event.is_set():
                msg = await connection.recv()
                
                # Log
                self.__logger.debug(f"Received message: {msg}") if self.__logger else None

                # Check if the message is a stop event
                if msg == Tag.STOP_EVENT:
                    self.__logger.debug("Stop event received. Stopping the server...") if self.__logger else None
                    self.__stop_event.set()

                # Check if the message is a parking event
                elif msg == Tag.PARKING_EVENT:
                    if self.__parking_event.is_set():
                        self.__logger.debug("Parking event received. Resuming processing...") if self.__logger else None
                        self.__parking_event.clear()
                    else:
                        self.__logger.debug("Parking event received. Pausing processing...") if self.__logger else None
                        self.__parking_event.set()
                    
                else:
                    # Unknown message type
                    self.__logger.warning(f"Unknown message type: {msg}") if self.__logger else None

                    await self._send_message(connection, Message(Tag.UNKNOWN_TAG, "Unknown message type received."))
                    continue

                # Broadcast the received message to all connected clients
                await self._broadcast_message(msg)

        except exceptions.ConnectionClosedOK:
            self.__logger.error(f"Client {connection.remote_address} disconnected gracefully.") if self.__logger else None

        except exceptions.ConnectionClosedError as e:
            self.__logger.error(f"Client {connection.remote_address} disconnected with error: {e}") if self.__logger else None

        except Exception as e:
            self.__logger.error(f"An unexpected error occurred with {connection.remote_address}: {e}") if self.__logger else None

        finally:
            # Remove the client from the set of connected clients
            self.__connected_clients.discard(connection)
            self.__logger.debug(f"Client {connection.remote_address} disconnected.") if self.__logger else None

    @final
    async def _send_message(self, connection, msg: Message):
        try:
            is_instance(msg, Message)
            await connection.send(str(msg))

        except Exception as e:
            self.__logger.error(f"Error sending message to {connection.remote_address}: {e}") if self.__logger else None

    @final
    async def _broadcast_message(self, msg: Message):
        if self.__connected_clients:  # Only broadcast if there are clients
            try:
                is_instance(msg, Message)
                await asyncio.gather(
                    *(client.send(str(msg)) for client in self.__connected_clients),
                    return_exceptions=True
                )
            
            except Exception as e:
                self.__logger.error(f"Unexpected error while broadcasting message: {e}") if self.__logger else None

    @final
    async def _broadcast_image_with_tag(self, tag: Tag, img: Image):
        try:
            # Open the image and convert it to a binary stream
            img_stream = io.BytesIO()
            img.save(img_stream, format=IMAGE_FORMAT)
            img_stream.seek(0)
            binary_data = img_stream.read()

            # Send the tagged binary data to the clients
            await self._broadcast_message(Message(tag, str(binary_data)))

        except Exception as e:
            self.__logger.error(f"Error sending image: {e}") if self.__logger else None

    @final
    async def broadcast_original_image(self, img: Image):
        """
        Broadcasts the original image to all connected clients.
        """
        await self._broadcast_image_with_tag(Tag.IMAGE_ORIGINAL, img)

    async def __broadcast_model_g_image(self, img: Image):
        """
        Broadcasts the image processed by model G to all connected clients.
        """
        await self._broadcast_image_with_tag(Tag.IMAGE_MODEL_G, img)

    async def __broadcast_model_m_image(self, img: Image):
        """
        Broadcasts the image processed by model M to all connected clients.
        """
        await self._broadcast_image_with_tag(Tag.IMAGE_MODEL_M, img)

    async def __broadcast_model_r_image(self, img: Image):
        """
        Broadcasts the image processed by model R to all connected clients.
        """
        await self._broadcast_image_with_tag(Tag.IMAGE_MODEL_R, img)

    @final
    async def broadcast_model_image(self, img: Image, model_name: str):
        if model_name == MODEL_G:
            await self.__broadcast_model_g_image(img)

        elif model_name == MODEL_M:
            await self.__broadcast_model_m_image(img)

        elif model_name == MODEL_R:
            await self.__broadcast_model_r_image(img)

        else:
            raise ValueError(f"Unknown model name: {model_name}")

    @final
    async def broadcast_serial_incoming_message(self, msg: str):
        is_instance(msg, str)

        # Send a tagged message
        await self._broadcast_message(Message(Tag.SERIAL_INCOMING_MESSAGE, msg))

    @final
    async def broadcast_serial_outgoing_message(self, msg: str):
        is_instance(msg, str)

        # Send a tagged message
        await self._broadcast_message(Message(Tag.SERIAL_OUTGOING_MESSAGE, msg))

    @final
    async def broadcast_rplidar_measures(self, msg: str):
        is_instance(msg, str)

        # Send a tagged message
        await self._broadcast_message(Message(Tag.RPLIDAR_MEASURES, msg))

    @final
    async def _loop(self):
        # Get the local IP address
        local_ip = get_local_ip()

        # Start the WebSocket server
        async with serve(self.__reactive_handler, self.__host, self.__port):
            self.__logger.info(f"WebSocket server started successfully on ws://{local_ip}:{self.__port}") if self.__logger else None
            await asyncio.get_running_loop().run_in_executor(None, self.__stop_event.wait)

        # Log the stopping of the server
        self.__logger.info("WebSocket server is stopping...") if self.__logger else None

    def __start(self):
        """
        Starts the WebSocket server in a separate thread.
        """
        with self.__rlock:
            # Clear the stop event
            self.__stop_event.clear()

    @final
    def is_running(self) -> bool:
        with self.__rlock:
            return not self.__stop_event.is_set()

    def __stop(self):
        """
        Stops the WebSocket server.
        """
        with self.__rlock:
            # Set the stop event
            self.__stop_event.set()

            # Set the thread to None
            self.__thread = None

    @final
    def is_stopped(self) -> bool:
        with self.__rlock:
            return not self.is_running()

    def create_thread(self):
        """
        Creates a thread to run the WebSocket server.
        """
        with self.__rlock:
            # Check if the server is already running
            if self.is_running():
                self.__logger.warning("WebSocket server is already running.") if self.__logger else None
                return

            # Start the server
            self.__start()

            # Create a thread to run the WebSocket server
            self.__thread = Thread(target=lambda: asyncio.run(self._loop()))
            self.__thread.start()

        # Log
        self.__logger.info("WebSocket server thread started.") if self.__logger else None
    
    def stop_thread(self):
        """
        Stops the WebSocket server thread.
        """
        with self.__rlock:
            # Check if the server is running
            if self.is_stopped():
                self.__logger.warning("WebSocket server is not running.") if self.__logger else None
                return

            # Stop the server
            self.__stop()

            # Wait for the thread to finish
            self.__thread.join()
            self.__thread = None

        # Log
        self.__logger.info("WebSocket server thread stopped.") if self.__logger else None

    @final
    def wait_stop_event(self):
        with self.__rlock:
            self.__stop_event.wait()

    @final
    def wait_parking_event(self):
        with self.__rlock:
            self.__parking_event.wait()

    def __del__(self):
        """
        Destructor to ensure the server is thread stopped when the object is deleted.
        """
        self.stop_thread() if self.is_running() else None
        self.__logger.info("WebsocketServer instance deleted.") if self.__logger else None