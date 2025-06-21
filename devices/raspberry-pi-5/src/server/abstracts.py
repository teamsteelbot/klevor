from abc import ABC, abstractmethod

from PIL.Image import Image

from .message import Message
from .enums import Tag

class WebsocketsServerABC(ABC):
    """
    Abstract class for a WebSocket server that handles real-time tracking updates.
    """

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
        Broadcasts a message to all connected clients.

        Args:
            msg (Message): The message to broadcast.
        """
        pass

    @abstractmethod
    async def _broadcast_image_with_tag(self, tag: Tag, img: Image):
        """
        Broadcasts an image with a tag to all the connected clients.

        Args:
            tag (Tag): The tag associated with the image.
            img (Image): The image to broadcast.
        """
        pass

    @abstractmethod
    def broadcast_original_image(self, img: Image):
        """
        Broadcasts the original image to all connected clients.

        Args:
            img (Image): The original image to broadcast.
        """
        pass

    @abstractmethod
    async def broadcast_model_image(self, img: Image, model_name: str):
        """
        Broadcasts the image processed by the specified model to all connected clients.

        Args:
            img (Image): The image to broadcast.
            model_name (str): The name of the model that processed the image.
        """
        pass

    @abstractmethod
    async def broadcast_serial_incoming_message(self, msg: str):
        """
        Broadcasts a serial incoming message to all connected clients.

        Args:
            msg (str): The serial incoming message to broadcast.
        """
        pass

    @abstractmethod
    async def broadcast_serial_outgoing_message(self, msg: str):
        """
        Broadcasts a serial outgoing message to all connected clients.

        Args:
            msg (str): The serial outgoing message to broadcast.
        """
        pass

    @abstractmethod
    async def broadcast_rplidar_measures(self, msg: str):
        """
        Broadcasts RPLIDAR measures to all connected clients.

        Args:
            msg (str): The RPLIDAR measures to broadcast.
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

    @abstractmethod
    async def _loop(self):
        """
        The main loop for the WebSocket server.
        """
        pass

    @abstractmethod
    def wait_stop_event(self):
        """
        Waits for the stop event to be set.
        """
        pass

    @abstractmethod
    def wait_parking_event(self):
        """
        Waits for the parking event to be set.
        """
        pass