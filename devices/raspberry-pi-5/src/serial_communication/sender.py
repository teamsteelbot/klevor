from typing import Optional, final
from queue import Empty, Queue
from multiprocessing import Event, RLock
from multiprocessing.synchronize import Event as EventCls
from time import sleep

from serial import Serial

from .common_messages import STOP_MESSAGE, OUTGOING_OK_MESSAGE, HEARTBEAT_MESSAGE
from .message import OutgoingMessage
from ..log import Logger
from ..log.decorators import log_on_error
from .constants import (
    RASPBERRY_PI_PICO_DATA_PORT,
    RASPBERRY_PI_PICO_DATA_PORT_ALT,
    RASPBERRY_PI_PICO_BAUDRATE,
    CONNECTION_ATTEMPTS,
    ATTEMPTS_DELAY,
    ENCODE,
    END_CHAR,
    STOP_TIMEOUT
)
from ..log.decorators import LoggerConsumerProtocol
from ..utils import is_instance
from ..server.dispatcher import Dispatcher as ServerDispatcher
from .abstracts import SenderABC


class Sender(SenderABC, LoggerConsumerProtocol):
    """
    Sender class to handle serial communication with the Raspberry Pi Pico.
    """

    # Logger configuration
    LOGGER_TAG = "SerialCommunicationSender"

    # Outgoing wait timeout
    OUTGOING_WAIT_TIMEOUT = 0.1

    def __init__(
        self,
        debug: bool,
        start_event: EventCls,
        stop_sent_event: EventCls,
        stop_confirmation_event: EventCls,
        stop_event: EventCls,
        messages_queue: Queue,
        writer_messages_queue: Queue,
        server_messages_queue: Optional[Queue] = None,
        data_port: Optional[str] = RASPBERRY_PI_PICO_DATA_PORT,
        data_port_alt: Optional[str] = RASPBERRY_PI_PICO_DATA_PORT_ALT,
        baudrate: Optional[int] = RASPBERRY_PI_PICO_BAUDRATE
    ):
        """
        Initialize the Receiver class.

        Args:
            debug (bool): Flag to indicate if the receiver is in debug mode.
            start_event (EventCls): Event to signal when the serial communication has started.
            stop_sent_event (EventCls): Event to signal when the stop message has been sent.
            stop_confirmation_event (EventCls): Event to signal when stop messages has been confirmed.
            stop_event (EventCls): Event to signal when the serial communication should stop sending and receiving messages.
            messages_queue (Queue): Queue to hold outgoing messages of the serial port.
            writer_messages_queue (Queue): Queue to hold log messages.
            server_messages_queue (Optional[Queue]): Queue to broadcast the messages through the websockets server.
            data_port (Optional[str]): Serial port used for sending data to Pico.
            data_port_alt (Optional[str]): Alternative serial port used for sending data to Pico.
            baudrate (Optional[int]): Baud rate for the serial communication.
        """
        # Initialize the debug flag
        self.__debug = debug

        # Initialize the queues and events
        self.__start_event = start_event
        self.__started_event = Event()
        self.__stop_event = stop_event
        self.__stop_sent_event = stop_sent_event
        self.__stop_confirmation_event = stop_confirmation_event
        self.__deleted_event = Event()
        self.__messages_queue = messages_queue

        # Initialize the logger
        self.__logger = Logger(
            writer_messages_queue,
            tag=self.LOGGER_TAG,
            debug=self.__debug
        )

        # Initialize the server dispatcher
        self.__server_dispatcher = ServerDispatcher(
            server_messages_queue,
            writer_messages_queue
        ) if server_messages_queue else None

        # Initialize the reentrant lock
        self.__rlock = RLock()

        # Check the type of data port and its alternative port
        is_instance(data_port, str)
        self.__data_port = data_port
        is_instance(data_port_alt, str)
        self.__data_port_alt = data_port_alt

        # Check the type of baudrate
        is_instance(baudrate, int)
        self.__baudrate = baudrate

        # Initialize the data serial port
        self.__data_serial = None

    @final
    @property
    def logger(self) -> Logger:
        return self.__logger

    @final
    def _open_port(self, port: str) -> None:
        try:
            self.__data_serial = Serial(port, self.__baudrate)
            self.__data_serial.flush()

        except Exception as e:
            raise RuntimeError(f"Error opening data {port}: {e}")

    @final
    def _start(self) -> None:
        with self.__rlock:
            # Check if the stop event is set
            if self.__stop_event.is_set():
                raise RuntimeError(
                    "Stop event is set. Serial communication sender will not run."
                )

            # Check if the serial communication sender is already running
            if self.__started_event.is_set():
                raise RuntimeError(
                    "Serial communication sender is already running. Cannot start again."
                )

            # Set the started event
            self.__started_event.set()

        # Open the data port
        attempt = 0
        for i in range(CONNECTION_ATTEMPTS):
            try:
                self._open_port(self.__data_port)
                if self.__data_serial.is_open:
                    attempt = i
                    break

            except Exception:
                try:
                    self._open_port(self.__data_port_alt)
                    if self.__data_serial.is_open:
                        attempt = i
                        break

                except Exception:
                    pass

            sleep(ATTEMPTS_DELAY)

        # Check if the data serial port is opened
        if not self.__data_serial or not self.__data_serial.is_open:
            raise RuntimeError(
                f"Failed to open data port on {self.__data_port} or {self.__data_port_alt} after {CONNECTION_ATTEMPTS} attempts."
            )

        # Flush the data serial port to ensure it is ready
        self.__data_serial.flush()

        # Log
        self.__logger.info(
            f"Data port opened on {self.__data_port} after {attempt + 1} {'attempts' if attempt != 0 else 'attempt'}."
        )

    @final
    def _stop(self) -> None:
        with self.__rlock:
            # Clear the started event
            self.__started_event.clear()

            # Check if the start event is set
            if self.__start_event.is_set():
                # Send the message to the serial port
                self._send_message(STOP_MESSAGE)

                # Set the stop sent event
                self.__stop_sent_event.set()

                # Wait for the confirmation message
                confirmation = self.__stop_confirmation_event.wait(STOP_TIMEOUT)
                if not confirmation:
                    self.__logger.warning(
                        "Stop confirmation event not set within the timeout."
                    )
                else:
                    self.logger.info(
                        "Stop confirmation event set."
                    )

                # Clear the stop confirmation event
                self.__stop_confirmation_event.clear()

                # Set the stop event
                self.__stop_event.set()

            # Close the data serial port
            if self.__data_serial and self.__data_serial.is_open:
                self.__data_serial.close()
                self.__data_serial = None

        # Log
        self.__logger.info("Stopped.")

    def _send_message(
        self,
        msg: OutgoingMessage
    ) -> None:
        # Log
        msg_str = str(msg)
        self.__logger.debug(
            f"Sending message: {msg_str}"
        )

        # Send the message to the serial port
        self.__data_serial.write(msg_str.encode(ENCODE))

        # Flush the serial port to ensure the message is sent
        self.__data_serial.flush()

    @final
    def _send_confirmation_message(self) -> None:
        self._send_message(OUTGOING_OK_MESSAGE)

    @final
    def _send_latest_message(self) -> OutgoingMessage | None:
        try:
            # Get the message from the queue
            msg = self.__messages_queue.get(
                timeout=self.OUTGOING_WAIT_TIMEOUT
            )

        except Empty:
            # Sent heartbeat message if the queue is empty
            self._send_message(HEARTBEAT_MESSAGE)
            return None

        # Send the message to the serial port
        self._send_message(msg)

        # If the server is set, send the message to the server
        self.__server_dispatcher.broadcast_serial_outgoing_message(
            str(msg).split(END_CHAR, 1)[0]
        ) if self.__server_dispatcher else None

    @final
    @log_on_error()
    def run(self) -> None:
        try:
            # Start the serial communication sender
            self._start()

            while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
                self._send_latest_message()

            # Stop
            self._stop()

        except Exception as e:
            # Stop the serial communication in case of an exception
            self._stop()
            raise e

    def __del__(self) -> None:
        """
        Destructor to clean up resources when the sender is no longer needed.
        """
        # Set the deleted event
        self.__deleted_event.set()

        # Log the deletion
        self.__logger.info("Instance will be deleted. Resources will be cleaned up.")