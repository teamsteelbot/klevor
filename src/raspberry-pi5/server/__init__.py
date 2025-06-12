import asyncio
import io
from threading import Thread
from multiprocessing import Event, RLock
from multiprocessing.synchronize import Event as EventCls
from typing import Optional

from websockets import serve, exceptions
from PIL.Image import Image

from log import Logger
from log.sub_logger import SubLogger
from utils import check_type, get_local_ip
from server.message import Message
from yolo import Yolo

class RealtimeTrackerServer:
    """
    A WebSocket server that handles real-time tracking updates.
    It allows clients to connect and receive messages about tracking events.

    This is only used on practices, not in the competition, to test new features and models in real-time.
    """
    # Logger configuration
    LOG_TAG = "RealtimeTrackerServer"

    # Server configuration
    HOST = '0.0.0.0'
    PORT = 8765

    # Connection status tag
    TAG_CONNECTION_STATUS = "connection_status"

    # Serial communication tags
    TAG_SERIAL_INCOMING_MESSAGE = "serial_incoming_message"
    TAG_SERIAL_OUTGOING_MESSAGE = "serial_outgoing_message"

    # Image tags
    TAG_IMAGE_ORIGINAL = "image_original"
    TAG_IMAGE_MODEL_G = "image_model_g"
    TAG_IMAGE_MODEL_M = "image_model_m"
    TAG_IMAGE_MODEL_R = "image_model_r"

    # RPLIDAR measures tag
    TAG_RPLIDAR_MEASURES = "rplidar_measures"

    # Event tags
    TAG_STOP_EVENT = "stop_event"
    TAG_PARKING_EVENT = "parking_event"
    
    # Tag separator
    TAG_SEPARATOR = ":"

    # Unknown message tag
    TAG_UNKNOWN_TAG = "unknown_tag"

    # Image format
    IMAGE_FORMAT = "JPEG"

    def __init__(
        self,
        parking_event: Optional[EventCls] = None,
        logger: Optional[Logger] = None,
        host: str = HOST,
        port: int = PORT
    ):
        """
        Initializes the WebSocket server with the specified host and port.

        Args:
            parking_event (Event|None): An event to signal when the server should pause processing.
            logger (Logger|None): Logger instance for logging messages.
            host (str): The host address for the WebSocket server. Default is 'localhost'.
            port (int): The port number for the WebSocket server. Default is 8765.
        """
        # Create a reentrant lock
        self.__rlock = RLock()
        
        # Create a stop event
        self.__stop_event = Event()
        self.__stop_event.set()

        # Check the type of parking event
        if parking_event:
            check_type(parking_event, Event)
        self.__parking_event = parking_event

        # Check the type of logger
        if logger:
            check_type(logger, Logger)

            # Get the sub-logger for this class
            self.__logger = SubLogger(logger, self.LOG_TAG)
        else:
            self.__logger = None

        # Check the type of host
        check_type(host, str)
        self.__host = host

        # Check the type of port
        check_type(port, int)
        self.__port = port

        # Initialize the connected clients set
        self.__connected_clients = set()

    def __log(self, message: str, log_to_file: bool = True, print_to_console: bool = True):
        """
        Logs a message using the logger if available.
        
        Args:
            message (str): The message to log.
            log_to_file (bool): Whether to log to file using the logger.
            print_to_console (bool): Whether to print the message to console.
        """
        if self.__logger and log_to_file:
            self.__logger.log(message)

        if print_to_console:
            print(f"{self.LOG_TAG}: {message}")

    async def __reactive_handler(self, connection) -> None:
        """
        Handles WebSocket connections and broadcasts messages to all clients.
        """
        # Add the client to the set of connected clients
        self.__connected_clients.add(connection)
        self.__log(f"Client connected: {connection.remote_address}")

        # Send a welcome message immediately upon connection
        await self._send_message(connection, Message(self.TAG_CONNECTION_STATUS, "Connected to RealtimeTrackerServer"))

        try:
            while True:
                message = await connection.recv()
                
                # Log
                self.__log(f"Received message: {message}", log_to_file=False)

                # Check if the message is a stop event
                if message == self.TAG_STOP_EVENT:
                    self.__log("Stop event received. Stopping the server...")
                    self.__stop_event.set()

                # Check if the message is a parking event
                elif message == self.TAG_PARKING_EVENT:
                    if not self.__parking_event:
                        pass

                    if self.__parking_event.is_set():
                        self.__log("Parking event received. Resuming processing...")
                        self.__parking_event.clear()
                    else:
                        self.__log("Parking event received. Pausing processing...")
                        self.__parking_event.set()
                    
                else:
                    # Unknown message type
                    self.__log(f"Unknown message type: {message}")

                    await self._send_message(connection, Message(self.TAG_UNKNOWN_TAG, "Unknown message type received."))
                    continue

                # Broadcast the received message to all connected clients
                await self._broadcast_message(message)

        except exceptions.ConnectionClosedOK:
            self.__log(f"Client {connection.remote_address} disconnected gracefully.")

        except exceptions.ConnectionClosedError as e:
            self.__log(f"Client {connection.remote_address} disconnected with error: {e}")

        except Exception as e:
            self.__log(f"An unexpected error occurred with {connection.remote_address}: {e}")

    async def _send_message(self, connection, message: Message):
        """
        Sends a message to a specific WebSocket connection.

        Args:
            connection: The WebSocket connection to send the message to.
            message (Message): The message to send.
        """
        try:
            check_type(message, Message)
            await connection.send(str(message))

        except Exception as e:
            self.__log(f"Error sending message to {connection.remote_address}: {e}")


    async def _broadcast_message(self, message: Message):
        """
        Broadcasts a message to all connected clients.

        Args:
            message (Message): The message to broadcast.
        """
        if self.__connected_clients:  # Only broadcast if there are clients
            try:
                check_type(message, Message)
                await asyncio.gather(*(client.send(str(message)) for client in self.__connected_clients))
            
            except Exception as e:
                self.__log(f"Unexpected error while broadcasting message: {e}")

    async def _broadcast_image_with_tag(self, tag: str, img: Image):
        """
        Broadcasts an image with a tag to all the connected clients.
        """
        try:
            # Open the image and convert it to a binary stream
            img_stream = io.BytesIO()
            img.save(img_stream, format=self.IMAGE_FORMAT)
            img_stream.seek(0)
            binary_data = img_stream.read()

            # Send the tagged binary data to the clients
            await self._broadcast_message(Message(tag, str(binary_data)))
            self.__log(f"Image with tag '{tag}' sent to the clients.")

        except Exception as e:
            self.__log(f"Error sending image: {e}")

    async def broadcast_image_original(self, img: Image):
        """
        Broadcasts the original image to all connected clients.
        """
        await self._broadcast_image_with_tag(self.TAG_IMAGE_ORIGINAL, img)

    async def __broadcast_image_model_g(self, img: Image):
        """
        Broadcasts the image processed by model G to all connected clients.
        """
        await self._broadcast_image_with_tag(self.TAG_IMAGE_MODEL_G, img)

    async def __broadcast_image_model_m(self, img: Image):
        """
        Broadcasts the image processed by model M to all connected clients.
        """
        await self._broadcast_image_with_tag(self.TAG_IMAGE_MODEL_M, img)

    async def __broadcast_image_model_r(self, img: Image):
        """
        Broadcasts the image processed by model R to all connected clients.
        """
        await self._broadcast_image_with_tag(self.TAG_IMAGE_MODEL_R, img)

    async def broadcast_image_model(self, img: Image, model_name: str):
        """
        Broadcasts the image processed by the specified model to all connected clients.

        Args:
            img (Image): The image to broadcast.
            model_name (str): The name of the model that processed the image.
        """
        if model_name == Yolo.MODEL_G:
            await self.__broadcast_image_model_g(img)

        elif model_name == Yolo.MODEL_M:
            await self.__broadcast_image_model_m(img)

        elif model_name == Yolo.MODEL_R:
            await self.__broadcast_image_model_r(img)

        else:
            raise ValueError(f"Unknown model name: {model_name}")

    async def broadcast_serial_incoming_message(self, message: str):
        """
        Broadcasts a serial incoming message to all connected clients.
        """
        check_type(message, str)

        # Send a tagged message
        await self._broadcast_message(Message(self.TAG_SERIAL_INCOMING_MESSAGE, message))

        # Log
        self.__log(f"Serial incoming message sent: {message}")

    async def broadcast_serial_outgoing_message(self, message: str):
        """
        Broadcasts a serial outgoing message to all connected clients.
        """
        check_type(message, str)

        # Send a tagged message
        await self._broadcast_message(Message(self.TAG_SERIAL_OUTGOING_MESSAGE, message))

        # Log
        self.__log(f"Serial outgoing message sent: {message}")

    async def broadcast_rplidar_measures(self, message: str):
        """
        Broadcasts RPLIDAR measures to all connected clients.

        Args:
            message (str): The RPLIDAR measures to broadcast.
        """
        check_type(message, str)

        # Send a tagged message
        await self._broadcast_message(Message(self.TAG_RPLIDAR_MEASURES, message))

        # Log
        self.__log(f"RPLIDAR measures sent")

    async def __loop(self):
        """
        The main loop for the WebSocket server.
        """
        # Get the local IP address
        local_ip = get_local_ip()

        # Start the WebSocket server
        self.__log(f"Starting WebSocket server on ws://{local_ip}:{self.__port}")
        async with serve(self.__reactive_handler, self.__host, self.__port):
            self.__log("WebSocket server started successfully.")
            await asyncio.get_running_loop().run_in_executor(None, self.__stop_event.wait)

        # Log the stopping of the server
        self.__log("WebSocket server is stopping...")

    def __stop(self):
        """
        Stops the WebSocket server.
        """
        with self.__rlock:
            if self.__stop_event.is_set():
                return

            # Set the stop event
            self.__stop_event.set()

            # Log the stopping event
            self.__log("WebSocket server stop event set. Stopping the server...")

    def create_thread(self):
        """
        Creates a thread to run the WebSocket server.
        """
        with self.__rlock:
            if self.is_running():
                self.__log("WebSocket server is already running.")
                return

            # Clear the stop event
            self.__stop_event.clear()

            # Create a thread to run the WebSocket server
            thread = Thread(target=lambda: asyncio.run(self.__loop()))
            thread.start()
    
    def stop_thread(self):
        """
        Stops the WebSocket server thread.
        """
        with self.__rlock:
            self.__stop()
        
    def is_running(self) -> bool:
        """
        Checks if the WebSocket server is running.

        Returns:
            bool: True if the server is running, False otherwise.
        """
        with self.__rlock:
            return not self.__stop_event.is_set()
    
    def is_stopped(self) -> bool:
        """
        Checks if the WebSocket server is stopped.

        Returns:
            bool: True if the server is stopped, False otherwise.
        """
        with self.__rlock:
            return not self.is_running()

    def __del__(self):
        """
        Destructor to ensure the server is thread stopped when the object is deleted.
        """
        self.stop_thread()