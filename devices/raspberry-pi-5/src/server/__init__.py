from queue import Empty
import asyncio
from multiprocessing import Event, Queue, RLock
from multiprocessing.synchronize import Event as EventCls
from threading import Thread
from typing import final

from PIL.Image import Image
from websockets import exceptions, serve

from .abstracts import WebSocketServerABC
from .constants import HOST, PORT
from .enums import Tag
from .message import Message
from ..log import Logger
from ..utils import get_local_ip, is_instance
from ..utils.decorators import ignore_sigint, log_method_error


class WebSocketServer(WebSocketServerABC):
    """
    Class for a WebSocket server that handles real-time tracking updates.
    It allows clients to connect and receive messages about tracking events.

    This is only used on practices, not in the competition, to test new features and models in real-time.
    """

    # Logger configuration
    LOGGER_TAG = "WebSocketServer"

    # Wait timeout
    WAIT_TIMEOUT = 0.1

    def __init__(
        self, messages_queue: Queue, parking_event: EventCls,
        stop_event: EventCls, writer_messages_queue: Queue,
        host: str = HOST, port: int = PORT
    ):
        """
        Initializes the WebSocket server with the specified host and port.

        Args:
            messages_queue (Queue): Queue to broadcast messages through the websockets server.
            parking_event (EventCls): Event to signal the parking state of the robot.
            stop_event (EventCls): Event to signal when the websockets server should stop.
            writer_messages_queue (Queue): Queue to hold log messages.
            host (str): The host address for the WebSocket server.
            port (int): The port number for the WebSocket server.
        """
        # Initialize the messages queue and events
        self.__messages_queue = messages_queue
        self.__opened_event = Event()
        self.__parking_event = parking_event
        self.__stop_event = stop_event

        # Initialize the logger
        self.__logger = Logger(writer_messages_queue, self.LOGGER_TAG)

        # Check the type of host
        is_instance(host, str)
        self.__host = host

        # Check the type of port
        is_instance(port, int)
        self.__port = port

        # Initialize the reentrant lock
        self.__rlock = RLock()

        # Initialize the connected clients set
        self.__connected_clients = set()

        # Initialize the broadcast thread
        self.__broadcast_thread = None

    @final
    async def _reactive_handler(self, connection) -> None:
        # Add the client to the set of connected clients
        self.__connected_clients.add(connection)
        self.__logger.debug(f"Client connected: {connection.remote_address}")

        # Send a welcome message immediately upon connection
        await self._send_message(
            connection, Message(
                Tag.CONNECTION_STATUS,
                "Connected to WebsocketServer"
            )
        )

        try:
            while not self.__stop_event.is_set():
                msg = await connection.recv()

                # Log
                self.__logger.debug(f"Received message: {msg}")

                # Check if the message is a stop event
                if msg == Tag.STOP_EVENT:
                    self.__logger.debug(
                        "Stop event received. Stopping the server..."
                    )
                    self.__stop_event.set()

                # Check if the message is a parking event
                elif msg == Tag.PARKING_EVENT:
                    if self.__parking_event.is_set():
                        self.__logger.debug(
                            "Parking event received. Resuming processing..."
                        )
                        self.__parking_event.clear()
                    else:
                        self.__logger.debug(
                            "Parking event received. Pausing processing..."
                        )
                        self.__parking_event.set()

                else:
                    # Unknown message type
                    self.__logger.warning(f"Unknown message type: {msg}")

                    await self._send_message(
                        connection,
                        Message(
                            Tag.UNKNOWN_TAG,
                            "Unknown message type received."
                        )
                    )
                    continue

                # Broadcast the received message to all connected clients
                await self._broadcast_message(msg)

        except exceptions.ConnectionClosedOK:
            self.__logger.error(
                f"Client {connection.remote_address} disconnected gracefully."
            )

        except exceptions.ConnectionClosedError as e:
            self.__logger.error(
                f"Client {connection.remote_address} disconnected with error: {e}"
            )

        except Exception as e:
            self.__logger.error(
                f"An unexpected error occurred with {connection.remote_address}: {e}"
            )

        finally:
            # Remove the client from the set of connected clients
            self.__connected_clients.discard(connection)
            self.__logger.debug(
                f"Client {connection.remote_address} disconnected."
            )

    @final
    async def _send_message(self, connection, msg: Message):
        try:
            # Check the type of connection
            is_instance(msg, Message)

            # Check if the connection is still open
            if connection.open:
                # Send the message to the client
                await connection.send(str(msg))

        except Exception as e:
            self.__logger.error(
                f"Error sending message to {connection.remote_address}: {e}"
            )

    @final
    async def _broadcast_message(self, msg: Message):
        if not self.__connected_clients:
            return

        try:
            # Check the type of msg
            is_instance(msg, Message)

            # Broadcast the message to all connected clients
            await asyncio.gather(
                *(client.send(str(msg)) for client in self.__connected_clients),
                return_exceptions=True
            )

        except Exception as e:
            self.__logger.error(
                f"Unexpected error while broadcasting message: {e}"
            )

    @final
    async def _broadcast_last_message(self) -> None:
        try:
            # Process any remaining messages in the queue
            msg = self.__messages_queue.get(timeout=self.WAIT_TIMEOUT)

            # Broadcast the last message to all connected clients
            await self._broadcast_message(msg)

        except Empty:
            # If the queue is empty, do nothing
            return None

    @final
    async def _broadcast_handler(self):
        while not self.__stop_event.is_set():
            # Broadcast the last message if available
            await self._broadcast_last_message()

        # Check if there are any remaining messages in the queue
        while not self.__messages_queue.empty():
            # Broadcast the last message if available
            await self._broadcast_last_message()

    @final
    @ignore_sigint
    @log_method_error('__logger')
    async def run(self):
        with self.__rlock:
            # Check if the stop event is set
            if self.__stop_event.is_set():
                self.__logger.warning(
                    "Stop event is set. WebSocket server will not run."
                )
                return

            # Check if the websocket server is already running
            if self.is_running():
                self.__logger.warning(
                    "WebSocket server is already running. Cannot start again."
                )
                return

            # Set the opened event to signal that the websocket server is ready
            self.__opened_event.set()

        # Get the local IP address
        local_ip = get_local_ip()

        # Create a thread to handle broadcasting messages
        self.__broadcast_thread = Thread(
            target=self._broadcast_handler
        )
        self.__broadcast_thread.start()

        # Start the WebSocket server
        self.__logger.debug("WebSocket server is starting...")
        async with serve(self._reactive_handler, self.__host, self.__port):
            self.__logger.info(
                f"WebSocket server started successfully on ws://{local_ip}:{self.__port}"
            )
            await asyncio.get_running_loop().run_in_executor(
                None,
                self.__stop_event.wait
            )

        # Wait for the broadcast thread to finish
        self.__broadcast_thread.join()
        self.__broadcast_thread = None

        # Clear the opened event
        with self.__rlock:
            self.__opened_event.clear()

        # Log the stopping of the server
        self.__logger.info("WebSocket server stopped.")

    @final
    def is_running(self) -> bool:
        with self.__rlock:
            return not self.__stop_event.is_set() and self.__opened_event.is_set()

    @final
    def is_stopped(self) -> bool:
        return not self.is_running()

    def __del__(self):
        """
        Destructor to clean up resources when the websockets server is no longer needed.
        """
        self.__stop_event.set()

        # Log
        self.__logger.debug(
            "WebSocket server instance is being deleted. Resources will be cleaned up."
        )
