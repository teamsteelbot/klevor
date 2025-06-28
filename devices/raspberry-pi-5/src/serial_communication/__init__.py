from queue import Empty
from multiprocessing import Event, Queue, RLock
from multiprocessing.synchronize import Event as EventCls
from multiprocessing.sharedctypes import Value as ValueCls
from threading import Thread
from time import sleep
from typing import Optional, final

from serial import Serial

from .abstracts import SerialCommunicationABC
from .constants import (
    ENCODE,
    RASPBERRY_PI_PICO_BAUDRATE,
    RASPBERRY_PI_PICO_CONSOLE_PORT,
    RASPBERRY_PI_PICO_CONSOLE_PORT_ALT,
    RASPBERRY_PI_PICO_DATA_PORT,
    RASPBERRY_PI_PICO_DATA_PORT_ALT,
    END_CHAR
)
from .enums import OutgoingCategory, Status
from .message import IncomingMessage, OutgoingMessage
from ..enums import Challenge
from ..log import Logger
from ..server.dispatcher import Dispatcher
from ..utils import is_instance
from ..utils.decorators import ignore_sigint
from ..log.decorators import log_on_error
from ..log.protocols import LoggerConsumerProtocol


class SerialCommunication(SerialCommunicationABC, LoggerConsumerProtocol):
    """
    Class to handle the serial communication through USB.
    """

    # Logger configuration
    LOGGER_TAG = "SerialCommunication"
    SENDER_LOGGER_TAG = f"{LOGGER_TAG}Sender"
    RECEIVER_LOGGER_TAG = f"{LOGGER_TAG}Receiver"

    # Incoming delay
    INCOMING_DELAY = 0.01

    # Outgoing wait timeout
    OUTGOING_WAIT_TIMEOUT = 0.1

    # Stop delay
    STOP_DELAY = 0.1

    # Confirmation timeout
    CONFIRMATION_TIMEOUT = 5.0
    CONFIRMATION_ATTEMPTS = CONFIRMATION_TIMEOUT // INCOMING_DELAY

    # Attempts to connect to the serial port
    CONNECTION_ATTEMPTS = 5

    # Attempts delay
    ATTEMPTS_DELAY = 1

    def __init__(
        self,
        debug: bool,
        challenge: ValueCls,
        start_event: EventCls,
        parking_event: EventCls,
        stop_event: EventCls,
        messages_queue: Queue,
        writer_messages_queue: Queue,
        bno08x_horizontal_axis_deg: ValueCls,
        bno08x_turns: ValueCls,
        photographer_capture_image_event: EventCls,
        server_messages_queue: Optional[Queue] = None,
        console_port: Optional[str] = RASPBERRY_PI_PICO_CONSOLE_PORT,
        console_port_alt: Optional[
            str] = RASPBERRY_PI_PICO_CONSOLE_PORT_ALT,
        data_port: Optional[str] = RASPBERRY_PI_PICO_DATA_PORT,
        data_port_alt: Optional[str] = RASPBERRY_PI_PICO_DATA_PORT_ALT,
        baudrate: Optional[int] = RASPBERRY_PI_PICO_BAUDRATE
    ):
        """
        Initialize the serial communication class.

        Args:
            debug (bool): Flag to indicate if the serial communication is in debug mode.
            challenge (ValueCls): Shared value for the challenge.
            start_event (EventCls): Event to signal when the serial communication has started.
            parking_event (EventCls): Event to signal the parking state of the robot.
            stop_event (EventCls): Event to signal when the serial communication should stop sending and receiving messages.
            messages_queue (Queue): Queue to hold outgoing messages to the serial port.
            writer_messages_queue (Queue): Queue to hold log messages.
            photographer_capture_image_event (EventCls): Event to signal when an image should be captured.
            bno08x_horizontal_axis_deg (ValueCls): Shared value for the BNO08X horizontal axis angle in degrees.
            bno08x_turns (ValueCls): Shared value for the BNO08X turns.
            server_messages_queue (Optional[Queue]): Queue to broadcast the messages through the websockets server.
            console_port (Optional[str]): Serial port used for receiving data from Pico.
            console_port_alt (Optional[str]): Alternative serial port used for receiving data from Pico.
            data_port (Optional[str]): Serial port used for sending data to Pico.
            data_port_alt (Optional[str]): Alternative serial port used for sending data to Pico.
            baudrate (Optional[int]): Baud rate for the serial communication.
        """
        # Initialize the debug flag
        self.__debug = debug

        # Initialize the values, queues and events
        self.__challenge = challenge
        self.__started_event = Event()
        self.__start_event = start_event
        self.__parking_event = parking_event
        self.__deleted_event = Event()
        self.__stop_event = stop_event
        self.__messages_queue = messages_queue
        self.__bno08x_horizontal_axis_deg = bno08x_horizontal_axis_deg
        self.__bno08x_turns = bno08x_turns
        self.__photographer_capture_image_event = photographer_capture_image_event

        # Initialize the loggers
        self.__logger = Logger(writer_messages_queue, self.LOGGER_TAG)
        self.__sender_logger = Logger(writer_messages_queue, self.SENDER_LOGGER_TAG)
        self.__receiver_logger = Logger(writer_messages_queue, self.RECEIVER_LOGGER_TAG)

        # Initialize the server dispatcher
        self.__server_dispatcher = Dispatcher(
            server_messages_queue,
            writer_messages_queue
        ) if server_messages_queue else None

        # Initialize the reentrant lock
        self.__rlock = RLock()

        # Check the type of console port and its alternative port
        is_instance(console_port, str)
        self.__console_port = console_port
        is_instance(console_port_alt, str)
        self.__console_port_alt = console_port_alt

        # Check the type of data port and its alternative port
        is_instance(data_port, str)
        self.__data_port = data_port
        is_instance(data_port_alt, str)
        self.__data_port_alt = data_port_alt

        # Check the type of baudrate
        is_instance(baudrate, int)
        self.__baudrate = baudrate

        # Initialize the console and data serial ports
        self.__console_serial = None
        self.__data_serial = None

        # Initialize the threads
        self.__receiving_thread = None
        self.__sending_thread = None

    @final
    @property
    def logger(self) -> Logger:
        return self.__logger
    
    @final
    def _open_console_port(self, port: str) -> None:
        """
        Open the console port for serial communication.

        Args:
            port (str): The serial port to open.
        """
        try:
            self.__console_serial = Serial(port, self.__baudrate)
            self.__console_serial.flush()

        except Exception as e:
            raise RuntimeError(f"Error opening console port {port}: {e}")
        
    @final
    def _open_data_port(self, port: str) -> None:
        """
        Open the data port for serial communication.

        Args:
            port (str): The serial port to open.
        """
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
                    "Stop event is set. Serial communication will not run."
                )

            # Check if the serial communication is already running
            if self.__started_event.is_set():
                raise RuntimeError(
                    "Serial communication is already running. Cannot start again."
                )

            # Set the started event
            self.__started_event.set()

        # Open the console port
        attempt = 0
        for i in range(self.CONNECTION_ATTEMPTS):
            try:
                self._open_console_port(self.__console_port)
                if self.__console_serial.is_open:
                    attempt = i
                    break

            except Exception:
                try:
                    self._open_console_port(self.__console_port_alt)
                    if self.__console_serial.is_open:
                        attempt = i
                        break

                except Exception:
                    pass
                
            sleep(self.ATTEMPTS_DELAY)

        # Check if the console serial port is opened
        if not self.__console_serial or not self.__console_serial.is_open:
            raise RuntimeError(
                f"Failed to open console serial port on {self.__console_port} or {self.__console_port_alt} after {self.CONNECTION_ATTEMPTS} attempts."
            )

        # Flush the console serial port to ensure it is ready
        self.__console_serial.flush()

        # Log
        self.__logger.info(
            f"Serial console port opened on {self.__console_port} after {attempt + 1} {'attempts' if attempt != 0 else 'attempt'}."
        )

        # Open the data port
        for i in range(self.CONNECTION_ATTEMPTS):
            try:
                self._open_data_port(self.__data_port)
                if self.__data_serial.is_open:
                    attempt = i
                    break

            except Exception:
                try:
                    self._open_data_port(self.__data_port_alt)
                    if self.__data_serial.is_open:
                        attempt = i
                        break

                except Exception:
                    pass
                
            sleep(self.ATTEMPTS_DELAY)

        # Check if the data serial port is opened
        if not self.__data_serial or not self.__data_serial.is_open:
            raise RuntimeError(
                f"Failed to open data serial port on {self.__data_port} or {self.__data_port_alt} after {self.CONNECTION_ATTEMPTS} attempts."
            )

        # Flush the data serial port to ensure it is ready
        self.__data_serial.flush()

        # Log
        self.__logger.info(
            f"Serial data port opened on {self.__data_port} after {attempt + 1} {'attempts' if attempt != 0 else 'attempt'}."
        )

    @final
    def _stop(self) -> None:
        with self.__rlock:
            # Clear the started event
            self.__started_event.clear()

            # Send the stop message to the serial port
            self._send_stop_message()

            # Set the stop event
            self.__stop_event.set()

            # Close the console serial port
            if self.__console_serial and self.__console_serial.is_open:
                self.__console_serial.close()
                self.__console_serial = None

            # Close the data serial port
            if self.__data_serial and self.__data_serial.is_open:
                self.__data_serial.close()
                self.__data_serial = None

        # Log
        self.__logger.info("Stopped.")

    @final
    def _receive_latest_message(self) -> (IncomingMessage | None):
        if self.__console_serial.in_waiting == 0:
            sleep(self.INCOMING_DELAY)
            return None

        # Parse the message from the serial port
        buffer = ""
        while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
            data = self.__console_serial.read(1).decode("utf-8", errors="ignore")
            if not data:
                continue
            if data == END_CHAR:
                break
            buffer += data

        # Check if the stop event is set or the deleted event is set
        if self.__stop_event.is_set() or self.__deleted_event.is_set():
            return None
        
        # If the buffer is empty, return None
        if not buffer:
            return None
        
        # Strip the buffer to remove any leading or trailing whitespace and convert it to a string
        msg_str = buffer.strip()

        # Log
        self.__receiver_logger.debug(
            f"Received message: '{msg_str}'"
        ) if self.__debug else None

        # Get the message from the string
        msg = IncomingMessage.from_string(msg_str)

        # If the server is set, send the message to the server
        self.__server_dispatcher.broadcast_serial_incoming_message(
            msg_str
        ) if self.__server_dispatcher else None

        return msg

    @final
    def _send_latest_message(self) -> OutgoingMessage | None:
        try:
            # Get the message from the queue
            msg = self.__messages_queue.get(
                timeout=self.OUTGOING_WAIT_TIMEOUT
            )

        except Empty:
            return None

        # Send the message to the serial port
        self._send_message(msg)

        # If the server is set, send the message to the server
        self.__server_dispatcher.broadcast_serial_outgoing_message(
            str(msg).split(END_CHAR, 1)[0]
        ) if self.__server_dispatcher else None

    def _send_message(
        self,
        msg: OutgoingMessage
    ) -> None:
        # Log
        msg_str = str(msg)
        self.__sender_logger.debug(
            f"Sending message: {msg_str}"
        ) if self.__debug else None

        # Send the message to the serial port
        self.__data_serial.write(msg_str.encode(ENCODE))

        # Flush the serial port to ensure the message is sent
        self.__data_serial.flush()

    @final
    def _send_confirmation_message(self) -> None:
        self._send_message(OutgoingMessage(OutgoingCategory.STATUS, Status.OK.parsed_name))

    @final
    def _wait_confirmation_message(
        self,
        msg_to_confirm: OutgoingMessage
    ) -> None:
        # Log
        self.__receiver_logger.debug(
            f"Waiting for confirmation message for: {msg_to_confirm}"
        ) if self.__debug else None

        # Wait for the confirmation message
        attempts = 0
        while attempts < self.CONFIRMATION_ATTEMPTS:
            msg = self._receive_latest_message()
            if msg is None:
                attempts += 1
                continue

            if msg.is_error():
                raise RuntimeError(
                    f"Received error message: {msg.content}"
                )
            elif msg.is_confirmation():
                # Log the confirmation message
                self.__receiver_logger.debug(
                    f"Received confirmation message: {msg.content}"
                ) if self.__debug else None
                return

        raise RuntimeError(
            f"Confirmation message for {msg_to_confirm} not received within timeout."
        )

    @final
    def _send_stop_message(self) -> None:
        stop_msg = OutgoingMessage(
            OutgoingCategory.STATUS, Status.STOP.parsed_name
        )

        # Send the message to the serial port
        self._send_message(stop_msg)

        # Wait for the confirmation message
        self._wait_confirmation_message(stop_msg)

    @final
    @log_on_error()
    def _receiving_message_handler(self) -> None:
        # Wait for the first END_CHAR message to be received to ensure the serial port is ready
        self.__receiver_logger.info(
            "Waiting for initial END_CHAR message to confirm serial communication is ready..."
        )
        while not self.__stop_event.is_set() and not self.__deleted_event.is_set() and self.__console_serial.in_waiting > 0:
            char = self.__console_serial.read(1).decode(ENCODE, errors="ignore")
            if not char:
                continue
            if char == END_CHAR:
                # Log
                self.__receiver_logger.info(
                    "Received initial END_CHAR message. Serial communication is ready."
                )
                break
            
        # Wait for the start message
        self.__receiver_logger.info(
            "Waiting for start event..."
        )
        while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
            try:
                msg = self._receive_latest_message()
                if msg is None:
                    continue

            except ValueError as e:
                # May receive some garbage data, so we catch the exception
                self.__receiver_logger.warning(
                    f"Received invalid message, may be garbage data: '{e}'"
                )
                continue

            if msg.is_error():
                raise RuntimeError(
                    f"Received error message: '{msg.content}'"
                )

            elif msg.is_challenge():
                # Log
                self.__receiver_logger.info("Received challenge message.")

                # Send a confirmation message
                self._send_confirmation_message()

                # Set the challenge as an environment variable
                with self.__challenge.get_lock():
                    self.__challenge = Challenge.from_string(msg.content).as_char

                # Continue to wait for the start event
                continue

            elif msg.is_start():
                # Log
                self.__receiver_logger.info("Received start event.")

                # Check if the challenge is set
                with self.__challenge.get_lock():
                    if self.__challenge.value != '':
                        raise RuntimeError(
                            "Challenge not set. Stopping communication."
                        )

                # Send a confirmation message
                self._send_confirmation_message()

                # Set the start event
                self.__start_event.set()
                break

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

            elif msg.is_bno08x_horizontal_axis():
                # Log
                self.__receiver_logger.debug(
                    f"Received BNO08X horizontal axis message: {msg.content}"
                ) if self.__debug else None

                # Update the BNO08X horizontal axis angle
                with self.__bno08x_horizontal_axis_deg.get_lock():
                    self.__bno08x_horizontal_axis_deg.value = float(msg.content)

            elif msg.is_bno08x_turns():
                # Log
                self.__receiver_logger.debug(
                    f"Received BNO08X turns message: {msg.content}"
                ) if self.__debug else None

                # Update the BNO08X turns
                with self.__bno08x_turns.get_lock():
                    self.__bno08x_turns.value = int(msg.content)

        # Log
        self.__receiver_logger.info("Stopped.")

    @final
    @log_on_error()
    def _sending_message_handler(self) -> None:
        # Wait for start event to be set
        self.__sender_logger.info("Waiting for start event...")
        self.__start_event.wait()
        self.__sender_logger.info("Started.")

        while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
            self._send_latest_message()

        # Log
        self.__sender_logger.info("Stopped.")

    @final
    @ignore_sigint
    def run(self) -> None:
        # Start the serial communication
        self._start()

        try:
            # Create the receiving thread
            self.__receiving_thread = Thread(
                target=self._receiving_message_handler
            )
            self.__receiving_thread.start()

            # Create the sending thread
            self.__sending_thread = Thread(target=self._sending_message_handler)
            self.__sending_thread.start()

            # Wait for the receiving thread to finish
            self.__receiving_thread.join()
            self.__receiving_thread = None

            # Wait for the sending thread to finish
            self.__sending_thread.join()
            self.__sending_thread = None

        except Exception as e:
            # Stop the serial communication in case of an exception
            self._stop()
            raise e

    def __del__(self):
        """
        Destructor to clean up resources when the SerialCommunication instance is deleted.
        """
        self.__deleted_event.set()

        # Log
        self.__logger.info(
            "Instance is being deleted. Resources will be cleaned up."
        )
