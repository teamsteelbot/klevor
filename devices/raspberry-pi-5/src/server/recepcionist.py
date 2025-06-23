from typing import final
import io
from multiprocessing import Queue
import uuid

from PIL.Image import Image

from ..log import Logger
from ..constants import IMAGE_FORMAT
from .abstracts import ReceptionistABC
from ..utils import is_instance
from ..server.enums import Tag
from ..server.message import Message
from ..constants import MODEL_G, MODEL_M, MODEL_R

class Receptionist(ReceptionistABC):
    """
    Class for a receptionist that handles broadcasting messages and images
    """

    # Logger configuration
    LOGGER_TAG = "Receptionist"

    def __init__(self, server_messages_queue: Queue, writer_messages_queue: Queue):
        """
        Initializes the Receptionist class.

        Args:
            server_messages_queue (Queue): Queue to broadcast messages through the websockets server.
            writer_messages_queue (Queue): Queue to hold log messages.
        """
        # Initialize the server messages queue
        self.__server_messages_queue = server_messages_queue

        # Initialize the logger
        self.__uuid = uuid.uuid4()
        self.__logger_tag = f"{self.LOGGER_TAG}_{self.__uuid}"
        self.__logger = Logger(writer_messages_queue, self.__logger_tag)

    @final
    async def _broadcast_message(self, msg: Message):
        # Check the type of message
        is_instance(msg, Message)

        # Put the message in the server messages queue
        self.__server_messages_queue.put(msg)

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