from multiprocessing import Event, Queue, RLock
from multiprocessing.sharedctypes import Value as ValueCls
from multiprocessing.synchronize import Event as EventCls
from time import sleep
from typing import Optional, final

from serial import Serial

from .abstracts import ReceiverABC
from .common_messages import STOP_MESSAGE
from .constants import (
    ATTEMPTS_DELAY,
    CONNECTION_ATTEMPTS,
    ENCODE,
    END_CHAR,
    RASPBERRY_PI_PICO_BAUDRATE,
    RASPBERRY_PI_PICO_CONSOLE_PORTS,
    STOP_TIMEOUT,
)
from .dispatcher import Dispatcher as SerialDispatcher
from .message import IncomingMessage, OutgoingMessage
from ..enums import Challenge
from ..log import Logger
from ..log.decorators import log_on_error
from ..log.protocols import LoggerConsumerProtocol
from ..server.dispatcher import Dispatcher as ServerDispatcher
from ..utils import is_instance


class Receiver(ReceiverABC, LoggerConsumerProtocol):
    """
    Receiver class to handle serial communication with the Raspberry Pi Pico.
    """

    # Logger configuration
    LOGGER_TAG = "SerialCommunicationReceiver"

    # Incoming delay
    INCOMING_DELAY = 0.01

    # Confirmation timeout
    CONFIRMATION_TIMEOUT = 5.0
    CONFIRMATION_ATTEMPTS = CONFIRMATION_TIMEOUT / INCOMING_DELAY

    # Read timeout
    READ_TIMEOUT = 0.5

    def __init__(
        self,
        debug: bool,
        challenge: ValueCls,
        start_event: EventCls,
        stop_sent_event: EventCls,
        stop_confirmation_event: EventCls,
        stop_event: EventCls,
        bno08x_yaw_deg: ValueCls,
        bno08x_turns: ValueCls,
        sender_messages_queue: Queue,
        writer_messages_queue: Queue,
        server_messages_queue: Optional[Queue] = None,
        console_ports: Optional[list[str]] = RASPBERRY_PI_PICO_CONSOLE_PORTS,
        baudrate: Optional[int] = RASPBERRY_PI_PICO_BAUDRATE
    ):
        """
        Initialize the Receiver class.

        Args:
            debug (bool): Flag to indicate if the receiver is in debug mode.
            challenge (ValueCls): Shared value to hold the current challenge.
            start_event (EventCls): Event to signal when the serial communication has started.
            stop_sent_event (EventCls): Event to signal when the stop message has been sent.
            stop_confirmation_event (EventCls): Event to signal when stop messages has been confirmed.
            stop_event (EventCls): Event to signal when the serial communication should stop sending and receiving messages.
            bno08x_yaw_deg (ValueCls): Shared value for the BNO08X yaw angle in degrees.
            bno08x_turns (ValueCls): Shared value for the BNO08X turns.
            sender_messages_queue (Queue): Queue to hold outgoing messages of the serial port.
            writer_messages_queue (Queue): Queue to hold log messages.
            server_messages_queue (Optional[Queue]): Queue to broadcast the messages through the websockets server.
            console_ports (Optional[list[str]]): List of serial ports used for receiving data from Pico.
            baudrate (Optional[int]): Baud rate for the serial communication.
        """
        # Initialize the debug flag
        self.__debug = debug

        # Initialize the queues, values and events
        self.__challenge = challenge
        self.__bno08x_yaw_deg = bno08x_yaw_deg
        self.__bno08x_turns = bno08x_turns
        self.__start_event = start_event
        self.__started_event = Event()
        self.__stop_sent_event = stop_sent_event
        self.__stop_confirmation_event = stop_confirmation_event
        self.__stop_waiting_confirmation_event = Event()
        self.__stop_event = stop_event
        self.__deleted_event = Event()

        # Initialize the logger
        self.__logger = Logger(
            writer_messages_queue,
            tag=self.LOGGER_TAG,
            debug=self.__debug
        )

        # Initialize the serial dispatcher
        self.__serial_dispatcher = SerialDispatcher(sender_messages_queue)

        # Initialize the server dispatcher
        self.__server_dispatcher = ServerDispatcher(
            server_messages_queue,
            writer_messages_queue
        ) if server_messages_queue else None

        # Initialize the reentrant lock
        self.__rlock = RLock()

        # Check the type of console ports
        is_instance(console_ports, list)
        self.__console_ports = console_ports

        # Check the type of baudrate
        is_instance(baudrate, int)
        self.__baudrate = baudrate

        # Initialize the console serial port
        self.__console_port = None
        self.__console_serial = None

    @final
    @property
    def logger(self) -> Logger:
        return self.__logger

    @final
    def _open_port(self, port: str) -> None:
        try:
            # Create a new Serial instance for the console port
            self.__console_serial = Serial(port, self.__baudrate, timeout=self.READ_TIMEOUT)
            self.__console_port = port
            self.__console_serial.flush()

        except Exception as e:
            raise RuntimeError(f"Error opening console port {port}: {e}")

    @final
    def _start(self) -> None:
        with self.__rlock:
            # Check if the stop event is set
            if self.__stop_event.is_set():
                raise RuntimeError(
                    "Stop event is set. Serial communication receiver will not run."
                )

            # Check if the serial communication receiver is already running
            if self.__started_event.is_set():
                raise RuntimeError(
                    "Serial communication receiver is already running. Cannot start again."
                )

            # Set the started event
            self.__started_event.set()

        # Open the console port
        for i in range(CONNECTION_ATTEMPTS):
            for port in self.__console_ports:
                try:
                    self._open_port(port)

                    # Log
                    self.__logger.info(
                        f"Console port opened on {self.__console_port} after {i + 1} {'attempts' if i != 0 else 'attempt'}."
                    )
                    return

                except Exception:
                    pass

            sleep(ATTEMPTS_DELAY)

        raise RuntimeError(
            f"Failed to open console port after {CONNECTION_ATTEMPTS} attempts."
        )
        

    @final
    def _stop(self) -> None:
        with self.__rlock:
            try:
                # Check if the start event is set
                if self.__started_event.is_set():
                    # Clear the started event
                    self.__started_event.clear()

                    # Wait for the stop sent event to be set
                    if not self.__stop_sent_event.wait(timeout=STOP_TIMEOUT):
                        self.__logger.warning(
                            "Stop sent event not set within timeout. "
                        )
                    else:
                        # Log the stop sent
                        self.__logger.info(
                            "Stop sent event set."
                        )

                    # Clear the stop sent event
                    self.__stop_sent_event.clear()

                    # Set the stop waiting confirmation event
                    self.__stop_waiting_confirmation_event.set()

                    # Wait for the stop confirmation event to be set
                    self._wait_confirmation_message(STOP_MESSAGE, attempts=STOP_TIMEOUT/self.INCOMING_DELAY)

                    # Set the stop confirmation event
                    self.__stop_confirmation_event.set()

                    # Clear the stop waiting confirmation event
                    self.__stop_waiting_confirmation_event.clear()

            except Exception as e:
                # Log the error
                self.__logger.error(
                    f"Error while stopping the serial communication receiver: {e}"
                )

            # Set the stop event
            self.__stop_event.set()

            # Clear the deleted event
            self.__deleted_event.clear()

            # Close the console serial port
            if self.__console_serial and self.__console_serial.is_open:
                self.__logger.info(
                    f"Closing console serial port: {self.__console_port}"
                )
                self.__console_serial.close()
                self.__console_serial = None

        # Log
        self.__logger.info("Stopped.")

    @final
    def _receive_latest_message(self) -> (IncomingMessage | None):
        if self.__console_serial.in_waiting == 0:
            sleep(self.INCOMING_DELAY)
            return None

        # Parse the message from the serial port
        buffer = ""
        while (not self.__stop_event.is_set() and not self.__deleted_event.is_set()) or self.__stop_waiting_confirmation_event.is_set():
            data = self.__console_serial.read(1).decode(
                ENCODE,
                errors="ignore"
            )
            if not data:
                continue
            if data == END_CHAR:
                break
            buffer += data

        # Check if the stop event is set or the deleted event is set
        if (self.__stop_event.is_set() or self.__deleted_event.is_set()) and not self.__stop_waiting_confirmation_event.is_set():
            return None

        # If the buffer is empty, return None
        if not buffer:
            return None

        # Strip the buffer to remove any leading or trailing whitespace and convert it to a string
        msg_str = buffer.strip()

        # Log
        # self.__logger.debug(f"Received message: '{msg_str}'")

        # Get the message from the string
        msg = IncomingMessage.from_string(msg_str)

        # Check if it's a debug message
        if msg.is_debug():
            # Log the debug message
            self.__logger.debug(
                f"Received debug message: {msg.content}"
            )
            return None

        # If the server is set, send the message to the server
        self.__server_dispatcher.broadcast_serial_incoming_message(
            msg_str
        ) if self.__server_dispatcher else None

        return msg

    def _wait_confirmation_message(
        self,
        msg_to_confirm: OutgoingMessage,
        attempts: int = CONFIRMATION_ATTEMPTS
    ) -> None:
        """
        Wait for a confirmation message from the serial port.
        
        Args:
            msg_to_confirm (OutgoingMessage): The message to confirm.
            attempts (int): The number of attempts to wait for the confirmation message.
        Raises:
            RuntimeError: If the confirmation message is not received within the timeout.
        """
        # Log
        self.__logger.debug(
            f"Waiting confirmation message for: {msg_to_confirm}"
        )

        # Wait for the confirmation message
        i = 0
        while i < attempts:
            msg = self._receive_latest_message()
            if msg is None:
                i += 1
                continue

            if msg.is_error():
                raise RuntimeError(
                    f"Received error message: {msg.content}"
                )
            elif msg.is_confirmation():
                # Log the confirmation message
                self.__logger.debug(
                    f"Received confirmation message: {msg.content}"
                )
                return

            else:
                # Log the received message
                self.__logger.debug(
                    f"Received message while waiting for confirmation: {msg}"
                )

        raise RuntimeError(
            f"Confirmation message for {msg_to_confirm} not received within timeout."
        )

    @final
    @log_on_error()
    def run(self) -> None:
        try:
            # Start the serial communication receiver
            self._start()

            # Wait for the first END_CHAR message to be received to ensure the serial port is ready
            self.__logger.info(
                f"Waiting for initial {repr(END_CHAR)} message to confirm serial communication is ready..."
            )
            while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
                if self.__console_serial.in_waiting == 0:
                    sleep(self.INCOMING_DELAY)
                    continue

                # Read a single character from the console
                char = self.__console_serial.read(1).decode(
                    ENCODE,
                    errors="ignore"
                    )
                if not char:
                    continue
                if char == END_CHAR:
                    break
            if self.__stop_event.is_set() or self.__deleted_event.is_set():
                # Stop the serial communication receiver
                self._stop()
                return

            # Log
            self.__logger.info(
                f"Received initial {repr(END_CHAR)} message. Serial communication is ready."
            )

            # Wait for the start message
            self.__logger.info(
                "Waiting for start event..."
            )
            while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
                try:
                    msg = self._receive_latest_message()
                    # If no message is received, continue to wait
                    if msg is None:
                        continue

                except ValueError as e:
                    # May receive some garbage data, so we catch the exception
                    raise RuntimeError(
                        f"Received invalid message, may be garbage data: '{e}'"
                    )

                if msg.is_error():
                    raise RuntimeError(
                        f"Received error message: '{msg.content}'"
                    )

                elif msg.is_challenge():
                    # Log
                    self.__logger.info("Received challenge message.")

                    # Send a confirmation message
                    self.__serial_dispatcher.send_confirmation_message()

                    # Set the challenge as an environment variable
                    with self.__challenge.get_lock():
                        self.__challenge.value = Challenge.from_string(
                            msg.content
                            ).as_char

                    # Continue to wait for the start event
                    continue

                elif msg.is_start():
                    # Log
                    self.__logger.info("Received start event.")

                    # Check if the challenge is set
                    if self.__challenge.value == Challenge.NONE.as_char:
                        raise RuntimeError(
                            "Challenge not set. Stopping communication."
                        )

                    # Send a confirmation message
                    self.__serial_dispatcher.send_confirmation_message()

                    # Set the start event
                    self.__start_event.set()
                    break

                else:
                    # Log the received message
                    self.__logger.debug(
                        f"Received message while waiting for start event: {msg}"
                    )

            while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
                try:
                    msg = self._receive_latest_message()
                    if msg is None:
                        continue

                except ValueError as e:
                    # May signal a bad code on the Pico or garbage data
                    self.__logger.warning(
                        f"Received invalid message error, skipping: '{e}'"
                    )
                    continue

                if msg.is_error():
                    raise RuntimeError(
                        f"Received error message: '{msg.content}'"
                    )

                elif msg.is_bno08x_yaw_deg():
                    # Log
                    self.__logger.debug(
                        f"Received BNO08X yaw degrees message: {msg.content}"
                    )

                    # Update the BNO08X horizontal axis angle
                    with self.__bno08x_yaw_deg.get_lock():
                        self.__bno08x_yaw_deg.value = float(msg.content)

                elif msg.is_bno08x_turns():
                    # Log
                    self.__logger.debug(
                        f"Received BNO08X turns message: {msg.content}"
                    )

                    # Update the BNO08X turns
                    with self.__bno08x_turns.get_lock():
                        self.__bno08x_turns.value = int(msg.content)

                else:
                    # Log the received message
                    self.__logger.debug(
                        f"Received message: {msg}"
                    )

            # Stop
            self._stop()

        except Exception as e:
            # Stop the serial communication receiver in case of an exception
            self._stop()
            raise e

    def __del__(self) -> None:
        """
        Destructor to clean up resources when the receiver is no longer needed.
        """
        # Set the deleted event
        self.__deleted_event.set()

        # Log the deletion
        self.__logger.info(
            "Instance will be deleted. Resources will be cleaned up."
            )
