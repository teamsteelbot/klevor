from multiprocessing import Event, Queue
from multiprocessing.sharedctypes import Value as ValueCls
from multiprocessing.synchronize import Event as EventCls
from threading import Thread
from typing import Optional, final

from .abstracts import SerialCommunicationABC
from .constants import (
    RASPBERRY_PI_PICO_BAUDRATE,
    RASPBERRY_PI_PICO_CONSOLE_PORTS,
    RASPBERRY_PI_PICO_DATA_PORTS,
)
from .receiver import Receiver
from .sender import Sender
from ..log import Logger
from ..log.protocols import LoggerConsumerProtocol
from ..utils.decorators import ignore_sigint


class SerialCommunication(SerialCommunicationABC, LoggerConsumerProtocol):
    """
    Class to handle the serial communication through USB.
    """

    # Logger configuration
    LOGGER_TAG = "SerialCommunication"

    def __init__(
        self,
        debug: bool,
        challenge: ValueCls,
        start_event: EventCls,
        stop_event: EventCls,
        bno08x_yaw_deg: ValueCls,
        bno08x_turns: ValueCls,
        sender_messages_queue: Queue,
        writer_messages_queue: Queue,
        server_messages_queue: Optional[Queue] = None,
        console_ports: Optional[list[str]] = RASPBERRY_PI_PICO_CONSOLE_PORTS,
        data_ports: Optional[list[str]] = RASPBERRY_PI_PICO_DATA_PORTS,
        baudrate: Optional[int] = RASPBERRY_PI_PICO_BAUDRATE
    ):
        """
        Initialize the serial communication class.

        Args:
            debug (bool): Flag to indicate if the receiver is in debug mode.
            challenge (ValueCls): Shared value to hold the current challenge.
            start_event (EventCls): Event to signal when the serial communication has started.
            stop_event (EventCls): Event to signal when the serial communication should stop sending and receiving messages.
            bno08x_yaw_deg (ValueCls): Shared value for the BNO08X yaw angle in degrees.
            bno08x_turns (ValueCls): Shared value for the BNO08X turns.
            sender_messages_queue (Queue): Queue to hold outgoing messages of the serial port.
            writer_messages_queue (Queue): Queue to hold log messages.
            server_messages_queue (Optional[Queue]): Queue to broadcast the messages through the websockets server.
            console_ports (Optional[list[str]]): List of serial ports used for receiving data from Pico.
            data_ports (Optional[list[str]]): List of serial ports used for sending data to Pico.
            baudrate (Optional[int]): Baud rate for the serial communication.
        """
        # Initialize the events
        self.__stop_sent_event = Event()
        self.__stop_confirmation_event = Event()
        self.__stop_event = stop_event

        # Initialize the serial communication receiver
        self.__serial_receiver = Receiver(
            debug=debug,
            challenge=challenge,
            start_event=start_event,
            stop_sent_event=self.__stop_sent_event,
            stop_confirmation_event=self.__stop_confirmation_event,
            stop_event=stop_event,
            bno08x_yaw_deg=bno08x_yaw_deg,
            bno08x_turns=bno08x_turns,
            sender_messages_queue=sender_messages_queue,
            writer_messages_queue=writer_messages_queue,
            server_messages_queue=server_messages_queue,
            console_ports=console_ports,
            baudrate=baudrate
        )

        # Initialize the serial communication sender
        self.__serial_sender = Sender(
            debug=debug,
            start_event=start_event,
            stop_sent_event=self.__stop_sent_event,
            stop_confirmation_event=self.__stop_confirmation_event,
            stop_event=stop_event,
            messages_queue=sender_messages_queue,
            writer_messages_queue=writer_messages_queue,
            server_messages_queue=server_messages_queue,
            data_ports=data_ports,
            baudrate=baudrate
        )

        # Initialize the logger
        self.__logger = Logger(writer_messages_queue, self.LOGGER_TAG)

        # Initialize the threads
        self.__receiving_thread = None
        self.__sending_thread = None

    @final
    @property
    def logger(self) -> Logger:
        return self.__logger

    @final
    @ignore_sigint
    def run(self) -> None:
        try:
            # Create the receiving thread
            self.__logger.info(
                "Starting the serial communication receiver thread."
            )
            self.__receiving_thread = Thread(
                target=self.__serial_receiver.run
            )
            self.__receiving_thread.start()

            # Create the sending thread
            self.__logger.info(
                "Starting the serial communication sender thread."
            )
            self.__sending_thread = Thread(target=self.__serial_sender.run)
            self.__sending_thread.start()

            # Wait for the receiving thread to finish
            self.__receiving_thread.join()
            self.__receiving_thread = None

            # Wait for the sending thread to finish
            self.__sending_thread.join()
            self.__sending_thread = None

        except Exception as e:
            # Set the stop event in case of an exception
            self.__stop_event.set()
            raise e

    def __del__(self):
        """
        Destructor to clean up resources when the SerialCommunication instance is deleted.
        """
        self.__stop_event.set()

        # Log
        self.__logger.info(
            "Instance is being deleted. Resources will be cleaned up."
        )
