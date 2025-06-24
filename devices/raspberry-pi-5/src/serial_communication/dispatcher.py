from multiprocessing import Queue
from typing import final

from .abstracts import DispatcherABC
from .constants import STOP_MESSAGE
from .enums import OutgoingCategory
from .message import IncomingMessage, OutgoingMessage
from ..log import Logger
from ..utils import is_instance


class Dispatcher(DispatcherABC):
    """
    Class for a dispatcher that handles incoming and outgoing messages.
    """

    # Logger configuration
    LOGGER_TAG = "Dispatcher"

    # Wait timeout
    WAIT_TIMEOUT = 0.1

    def __init__(
        self,
        serial_incoming_messages_queue: Queue,
        serial_outgoing_messages_queue: Queue,
        writer_messages_queue: Queue
    ) -> None:
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
        self.__logger = Logger(
            writer_messages_queue, self.LOGGER_TAG,
            unique_tag=True
        )

    @final
    def receive_message(self) -> IncomingMessage | None:
        # Get the message from the queue
        return self.__serial_incoming_messages_queue.get(
            timeout=self.WAIT_TIMEOUT
        )

    @final
    def _send_message(self, msg: OutgoingMessage) -> None:
        # Check the type of message
        is_instance(msg, OutgoingMessage)

        # Put the message in the queue
        self.__serial_outgoing_messages_queue.put(msg)

    @final
    def send_motor_speed_message(self, speed: float) -> None:
        # Create the message
        msg = OutgoingMessage(OutgoingCategory.MOTOR_SPEED, str(speed))

        # Send the message
        self._send_message(msg)

    @final
    def send_servo_angle_message(self, angle: float) -> None:
        # Create the message
        msg = OutgoingMessage(OutgoingCategory.SERVO_ANGLE, str(angle))

        # Send the message
        self._send_message(msg)

    @final
    def send_stop_message(self) -> None:
        self._send_message(STOP_MESSAGE)
