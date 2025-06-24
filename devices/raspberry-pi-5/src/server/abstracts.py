from abc import ABC, abstractmethod

from PIL.Image import Image

from .enums import Tag
from .message import Message
from ..rplidar import Measure


class WebSocketServerABC(ABC):
    """
    Abstract class for a WebSocket server that handles real-time tracking updates.
    """

    @abstractmethod
    async def _reactive_handler(self, connection) -> None:
        """
        Handles WebSocket connections and messages.

        Args:
            connection: The WebSocket connection object.
        """
        pass

    @abstractmethod
    async def _send_message(self, connection, msg: Message):
        """
        Sends a message to a specific WebSocket connection.

        Args:
            connection: The WebSocket connection to send the message to.
            msg (Message): The message to send.
        """
        pass

    @abstractmethod
    async def _broadcast_message(self, msg: Message):
        """
        Broadcasts a message to all connected WebSocket clients.

        Args:
            msg (Message): The message to broadcast.
        """
        pass

    @abstractmethod
    async def _broadcast_last_message(self) -> None:
        """
        Processes the last message in the queue and broadcasts it to all connected clients.
        """
        pass

    @abstractmethod
    async def _broadcast_handler(self):
        """
        Continuously checks the messages queue and broadcasts the last message
        to all connected clients until the stop event is set.
        """
        pass

    @abstractmethod
    async def run(self):
        """
        Starts the WebSocket server and listens for incoming connections and messages.
        """
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """
        Checks if the WebSocket server is running.

        Returns:
            bool: True if the server is running, False otherwise.
        """
        pass

    @abstractmethod
    def is_stopped(self) -> bool:
        """
        Checks if the WebSocket server is stopped.

        Returns:
            bool: True if the server is stopped, False otherwise.
        """
        pass


class DispatcherABC:
    """
    Abstract class for a dispatcher that handles broadcasting messages
    and images
    """

    @abstractmethod
    def _broadcast_message(self, msg: Message):
        """
        Add a message to the messages queue to be sent to all connected clients.

        Args:
            msg (Message): The message to broadcast.
        """
        pass

    @abstractmethod
    def _broadcast_image_with_tag(self, tag: Tag, img: Image):
        """
        Adds an image with a specific tag to the messages queue to be sent to all connected clients.

        Args:
            tag (Tag): The tag associated with the image.
            img (Image): The image to broadcast.
        """
        pass

    @abstractmethod
    def broadcast_original_image(self, img: Image):
        """
        Adds the original image to the messages queue to be sent to all connected clients.

        Args:
            img (Image): The original image to broadcast.
        """
        pass

    @abstractmethod
    def broadcast_model_image(self, img: Image, model_name: str):
        """
        Adds a model-processed image to the messages queue to be sent to all connected clients.

        Args:
            img (Image): The image to broadcast.
            model_name (str): The name of the model that processed the image.
        """
        pass

    @abstractmethod
    def broadcast_serial_incoming_message(self, msg: str):
        """
        Adds a serial incoming message to the messages queue to be sent to all connected clients.

        Args:
            msg (str): The serial incoming message to broadcast.
        """
        pass

    @abstractmethod
    def broadcast_serial_outgoing_message(self, msg: str):
        """
        Adds a serial outgoing message to the messages queue to be sent to all connected clients.

        Args:
            msg (str): The serial outgoing message to broadcast.
        """
        pass

    @abstractmethod
    def broadcast_rplidar_measure(self, measure: Measure):
        """
        Adds a RPLIDAR measure to the messages queue to be sent to all connected clients.

        Args:
            measure (Measure): The RPLIDAR measure to broadcast.
        """
        pass
