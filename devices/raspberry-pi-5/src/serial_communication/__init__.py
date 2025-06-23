from multiprocessing import Event, Queue, RLock
from threading import Thread
from time import sleep
from typing import Optional, final

from serial import Serial, SerialException

from .abstracts import SerialCommunicationABC
from .constants import (
    RASPBERRY_PI_PICO_CONSOLE_PORT, RASPBERRY_PI_PICO_CONSOLE_PORT_ALT,
    RASPBERRY_PI_PICO_DATA_PORT, RASPBERRY_PI_PICO_DATA_PORT_ALT,
    RASPBERRY_PI_PICO_BAUDRATE, ENCODE
)
from .enums import OutgoingCategory, Status
from .message import IncomingMessage, OutgoingMessage
from ..env import Env
from ..env.enums import Challenge
from ..log import Logger
from ..server.dispatcher import Dispatcher
from ..utils import is_instance


class SerialCommunication(SerialCommunicationABC):
    """
    Class to handle the serial communication through USB.
    """

    # Logger configuration
    LOGGER_TAG = "SerialCommunication"

    # Incoming delay
    INCOMING_DELAY = 0.01

    # Outgoing wait timeout
    OUTGOING_WAIT_TIMEOUT = 0.1

    # Stop delay
    STOP_DELAY = 0.1

    def __init__(
            self,
            start_event: Event,
            parking_event: Event,
            stop_event: Event,
            incoming_messages_queue: Queue,
            outgoing_messages_queue: Queue,
            writer_messages_queue: Queue,
            photographer_capture_image_event: Event,
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
            start_event (Event): Event to signal when the serial communication has started.
            parking_event (Event): Event to signal the parking state of the robot.
            stop_event (Event): Event to signal when the serial communication should stop sending and receiving messages.
            incoming_messages_queue (Queue): Queue to hold incoming messages from the serial port.
            outgoing_messages_queue (Queue): Queue to hold outgoing messages to the serial port.
            writer_messages_queue (Queue): Queue to hold log messages.
            photographer_capture_image_event (Event): Event to signal when an image should be captured.
            server_messages_queue (Optional[Queue]): Queue to broadcast the messages through the websockets server.
            console_port (Optional[str]): Serial port used for receiving data from Pico.
            console_port_alt (Optional[str]): Alternative serial port used for receiving data from Pico.
            data_port (Optional[str]): Serial port used for sending data to Pico.
            data_port_alt (Optional[str]): Alternative serial port used for sending data to Pico.
            baudrate (Optional[int]): Baud rate for the serial communication.
        """
        # Initialize the queues and events
        self.__opened_event = Event()
        self.__start_event = start_event
        self.__parking_event = parking_event
        self.__stop_event = stop_event
        self.__incoming_messages_queue = incoming_messages_queue
        self.__outgoing_messages_queue = outgoing_messages_queue
        self.__photographer_capture_image_event = photographer_capture_image_event

        # Initialize the logger
        self.__logger = Logger(writer_messages_queue, self.LOGGER_TAG)
        
        # Initialize the server dispatcher
        self.__server_dispatcher = Dispatcher(
            server_messages_queue, writer_messages_queue) if server_messages_queue else None

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

        # Get the debug environment variable
        self.__debug = Env.get_debug_mode()

    @final
    def _open(self) -> None:
        # Clear the start event
        self.__start_event.clear()

        # Open the console port
        try:
            self.__console_serial = Serial(self.__console_port, self.__baudrate)

        except SerialException as port_e:
            # Try its alternative port
            try:
                self.__console_serial = Serial(self.__console_port_alt,
                                               self.__baudrate)

            except SerialException as port_alt_e:
                raise RuntimeError(
                    f"Error opening serial console port: {port_e} and alternative port: {port_alt_e}")

            raise RuntimeError(
                f"Error opening serial console port: {port_e}")

        # Open the data port
        try:
            self.__data_serial = Serial(self.__data_port, self.__baudrate)

        except SerialException as port_e:
            # Try its alternative port
            try:
                self.__data_serial = Serial(self.__data_port_alt,
                                            self.__baudrate)

            except SerialException as port_alt_e:
                raise RuntimeError(
                    f"Error opening serial data port: {port_e} and alternative port: {port_alt_e}")

            raise RuntimeError(f"Error opening serial data port: {port_e}")

        # Log
        self.__logger.info(
            f"Serial console port and data port opened with baudrate {self.__baudrate}.") if self.__logger else None

    @final
    def is_open(self) -> bool:
        with (self.__rlock):
            return not self.__stop_event.is_set() and self.__console_serial and self.__console_serial.is_open and self.__data_serial and self.__data_serial.is_open

    @final
    def is_closed(self) -> bool:
        return not self.is_open()
    
    @final
    def has_started(self) -> bool:
        with self.__rlock:
            return self.__start_event.is_set()

    @final
    def _put_incoming_message(self, msg: IncomingMessage) -> None:
        # Put the message in the queue
        self.__incoming_messages_queue.put(msg)

        # Log
        msg_str = str(msg)
        first_line = str(msg).split('\n')[0]
        self.__logger.debug(
            f"Received message: {first_line}") if self.__logger and self.__debug else None

        # If the server is set, send the message to the server
        self.__server_dispatcher.broadcast_serial_incoming_message(
            msg_str) if self.__server_dispatcher else None

    @final
    def _get_outgoing_message(self) -> OutgoingMessage | None:
        # Get the message from the queue
        msg = self.__outgoing_messages_queue.get(timeout=self.OUTGOING_WAIT_TIMEOUT)
        if msg is None:
            return None

        # Log
        first_line = str(msg).split('\n')[0]
        self.__logger.debug(
            f"Sending message: {first_line}") if self.__logger and self.__debug else None

        # If the server is set, send the message to the server
        self.__server_dispatcher.broadcast_serial_outgoing_message(
            first_line) if self.__server_dispatcher else None

        return msg
    
    @final
    def _send_confirmation_message(self) -> None:
        """
        Send a confirmation message to the console port.
        """
        # Create a confirmation message
        confirmation_msg = OutgoingMessage(OutgoingCategory.STATUS, Status.OK)

        # Put the message in the outgoing messages queue
        self.__outgoing_messages_queue.put(confirmation_msg)

    @final
    def _receiving_message_handler(self) -> None:
        # Log
        self.__logger.info(
            f"Serial port receiving handler started for port {self.__console_port}.") if self.__logger else None

        # Check if there is an initialization message received
        while self.is_open():
            if self.__console_serial.in_waiting > 0:
                console_msg = self.__console_serial.read(
                    self.__console_serial.in_waiting).decode(ENCODE).strip()
                self.__logger.debug(
                    "Received initialization message: " + console_msg) if self.__logger and self.__debug else None

                # Get the Message from the string
                msg = IncomingMessage.from_string(console_msg)

                # Check if the message is a start message
                if msg.is_start():
                    # Check if the challenge is set
                    if not Env.has_challenge():
                        # Stop the communication
                        self.__stop_event()

                        # Log
                        self.__logger.error(
                            "Challenge not set. Stopping communication.") if self.__logger else None
                        return

                    # Send a confirmation message
                    self._send_confirmation_message()

                    # Set the start event
                    self.__start_event.set()

                    # Log
                    self.__logger.info(
                        "Received start event.") if self.__logger else None
                    break

                elif msg.is_challenge():
                    # Send a confirmation message
                    self._send_confirmation_message()

                    # Set the challenge as an environment variable
                    Env.set_challenge(Challenge.from_string(msg.content))

                    # Log
                    self.__logger.info(
                        "Received challenge message.") if self.__logger else None
                    # Continue to wait for the start event
                    continue

        while self.is_open():
            if self.__console_serial.in_waiting == 0:
                sleep(self.INCOMING_DELAY)
                continue

            # Parse the message from the serial port
            msg_str = self.__console_serial.readline().decode(ENCODE).strip()
            msg = IncomingMessage.from_string(msg_str)

            if msg.is_stop():
                # Send a confirmation stop message
                self._send_confirmation_message()

                # Log the stop message
                self.__logger.info(
                    "Received stop event.") if self.__logger else None

                # Wait for a short time to ensure the message is sent
                sleep(self.STOP_DELAY)
                break

            elif msg.is_error():
                # Log the error message
                self.__logger.error(
                    f"Received error message: {msg.content}") if self.__logger else None

            # Put the message in the incoming messages queue
            self._put_incoming_message(msg)
            
        # Set the stop event to signal that the receiving handler has stopped
        self.__stop_event.set()

        # Clear the start event
        self.__start_event.clear()
        
        # Close the console serial port
        if self.__console_serial and self.__console_serial.is_open:
            self.__console_serial.close()
            self.__console_serial = None
            
        # Log
        self.__logger.info(
            f"Serial port receiving handler stopped for port {self.__console_port}.") if self.__logger else None

    @final
    def _sending_message_handler(self) -> None:
        # Log 
        self.__logger.info(
            "Waiting for start event on receiving handler...") if self.__logger else None

        # Wait for start event to be set
        self.__start_event.wait()

        # Log
        self.__logger.info(
            f"Serial port sending handler started for port {self.__data_port}.") if self.__logger else None

        while self.is_open():
            # Get the message from the queue
            msg = self._get_outgoing_message()
            if not msg:
                continue

            # Send the message to the serial port
            self.__data_serial.write(str(msg).encode(ENCODE))

            # Flush the serial port to ensure the message is sent
            self.__data_serial.flush()

        # Set the stop event to signal that the sending handler has stopped
        self.__stop_event.set()

        # Clear the start event
        self.__start_event.clear()

        # Close the data serial port
        if self.__data_serial and self.__data_serial.is_open:
            self.__data_serial.close()
            self.__data_serial = None

        # Log
        self.__logger.info(
            f"Serial port sending handler stopped for port {self.__data_port}.") if self.__logger else None

    @final
    def run(self) -> None:
        with self.__rlock:
            # Check if the stop event is set
            if self.__stop_event.is_set():
                self.__logger.warning(
                    "Stop event is set. Serial communication will not run.")
                return
    
            # Check if the websocket server is already running
            if self.is_open():
                self.__logger.warning(
                    "Serial communication is already running. Cannot start again.")
                return
    
            # Set the opened event to signal that the websocket server is ready
            self.__opened_event.set()

        # Create the receiving thread
        self.__receiving_thread = Thread(
            target=self._receiving_message_handler)
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

        # Clear the opened event
        with self.__rlock:
            self.__opened_event.clear()

    def __del__(self):
        """
        Destructor to clean up resources when the SerialCommunication instance is deleted.
        """
        self.__stop_event.set()
