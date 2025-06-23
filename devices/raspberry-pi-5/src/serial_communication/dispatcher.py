from multiprocessing import Queue
from typing import final

from ..log import Logger
from .abstracts import DispatcherABC
from .message import IncomingMessage, OutgoingMessage
from .enums import RPLIDAR, OutgoingCategory
from ..utils import is_instance

class Dispatcher(DispatcherABC):
    """
    Class for a dispatcher that handles incoming and outgoing messages.
    """

    # Logger configuration
    LOGGER_TAG = "Dispatcher"

    # Wait timeout
    WAIT_TIMEOUT = 0.1

    def __init__(self, serial_incoming_messages_queue: Queue,
                 serial_outgoing_messages_queue: Queue,
                 writer_messages_queue: Queue):
        """
        Initializes the Dispatcher class.

        Args:
            serial_incoming_messages_queue (Queue): Queue to hold incoming messages from the serial port.
            serial_outgoing_messages_queue (Queue): Queue to hold outgoing messages to the serial port.
            writer_messages_queue (Queue): Queue to hold log messages.
        """
        # Initialize the queues
        self.__serial_incoming_messages_queue = serial_incoming_messages_queue
        self.__serial_outgoing_messages_queue = serial_outgoing_messages_queue

        # Initialize the logger
        self.__logger = Logger(writer_messages_queue, self.LOGGER_TAG,
                               unique_tag=True)

    @final
    def receive_message(self) -> IncomingMessage | None:
        # Get the message from the queue
        return self.__serial_incoming_messages_queue.get(timeout=self.WAIT_TIMEOUT)

    @final
    def _send_message(self, msg: OutgoingMessage) -> None:
        # Check the type of message
        is_instance(msg, OutgoingMessage)

        # Put the message in the queue
        self.__serial_outgoing_messages_queue.put(msg)

    @final
    def send_rplidar_measures(self, measures: dict[RPLIDAR, float]) -> None:
        for key, value in measures.items():
            # Check the type of key and value
            is_instance(key, RPLIDAR)
            is_instance(value, float)

            # Create a message with the RPLIDAR measures type
            msg = OutgoingMessage(OutgoingCategory.RPLIDAR,
                                  f"{key.parsed_name}{OutgoingMessage.CONTENT_HEADER_SEPARATOR}{value}")

            # Put the message in the outgoing messages queue
            self._send_message(msg)