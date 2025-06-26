from queue import Empty
from multiprocessing import Event, Queue, RLock, Value
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
)
from .enums import OutgoingCategory, Status
from .message import IncomingMessage, OutgoingMessage
from ..env import Env
from ..env.enums import Challenge
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
        start_event: EventCls,
        parking_event: EventCls,
        stop_event: EventCls,
        incoming_messages_queue: Queue,
        outgoing_messages_queue: Queue,
        writer_messages_queue: Queue,
        bno08x_yaw_deg: ValueCls,
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
            start_event (EventCls): Event to signal when the serial communication has started.
            parking_event (EventCls): Event to signal the parking state of the robot.
            stop_event (EventCls): Event to signal when the serial communication should stop sending and receiving messages.
            incoming_messages_queue (Queue): Queue to hold incoming messages from the serial port.
            outgoing_messages_queue (Queue): Queue to hold outgoing messages to the serial port.
            writer_messages_queue (Queue): Queue to hold log messages.
            photographer_capture_image_event (EventCls): Event to signal when an image should be captured.
            bno08x_yaw_deg (ValueCls): Shared value for the BNO08X yaw angle in degrees.
            bno08x_turns (ValueCls): Shared value for the BNO08X turns.
            server_messages_queue (Optional[Queue]): Queue to broadcast the messages through the websockets server.
            console_port (Optional[str]): Serial port used for receiving data from Pico.
            console_port_alt (Optional[str]): Alternative serial port used for receiving data from Pico.
            data_port (Optional[str]): Serial port used for sending data to Pico.
            data_port_alt (Optional[str]): Alternative serial port used for sending data to Pico.
            baudrate (Optional[int]): Baud rate for the serial communication.
        """
        # Initialize the values, queues and events
        self.__opened_event = Event()
        self.__start_event = start_event
        self.__parking_event = parking_event
        self.__stop_event = stop_event
        self.__incoming_messages_queue = incoming_messages_queue
        self.__outgoing_messages_queue = outgoing_messages_queue
        self.__bno08x_yaw_deg = bno08x_yaw_deg
        self.__bno08x_turns = bno08x_turns
        self.__photographer_capture_image_event = photographer_capture_image_event

        # Initialize the logger
        self.__logger = Logger(writer_messages_queue, self.LOGGER_TAG)

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

        # Get the debug environment variable
        self.__debug = Env.get_debug_mode()

    @final
    @property
    def logger(self) -> Logger:
        return self.__logger

    @final
    def _open(self) -> None:
        # Clear the start event
        self.__start_event.clear()

        try:
            # Open the console port
            for _ in range(self.CONNECTION_ATTEMPTS):
                try:
                    self.__console_serial = Serial(self.__console_port, self.__baudrate)

                except Exception as port_e:
                    # Try its alternative port
                    try:
                        self.__console_serial = Serial(
                            self.__console_port_alt,
                            self.__baudrate
                        )

                    except Exception as port_alt_e:
                        raise RuntimeError(
                            f"Error opening serial console port: {port_e} and alternative port: {port_alt_e}"
                        )

                    raise RuntimeError(
                        f"Error opening serial console port: {port_e}"
                    )
                
                if self.__console_serial.is_open:
                    # Flush the console serial port to ensure it is ready
                    self.__console_serial.flush()
                    break
                sleep(self.ATTEMPTS_DELAY)

            # Open the data port
            for _ in range(self.CONNECTION_ATTEMPTS):
                try:
                    self.__data_serial = Serial(self.__data_port, self.__baudrate)

                except Exception as port_e:
                    # Try its alternative port
                    try:
                        self.__data_serial = Serial(
                            self.__data_port_alt,
                            self.__baudrate
                        )

                    except Exception as port_alt_e:
                        raise RuntimeError(
                            f"Error opening serial data port: {port_e} and alternative port: {port_alt_e}"
                        )

                    raise RuntimeError(f"Error opening serial data port: {port_e}")
                
                if self.__data_serial.is_open:
                    # Flush the data serial port to ensure it is ready
                    self.__data_serial.flush()
                    break
                sleep(self.ATTEMPTS_DELAY)
                
        except Exception as e:
            # If there is an error opening the serial ports, set the stop event
            self.__stop_event.set()

            # Set the start event to unblock the waiting threads
            self.__start_event.set()

            # Raise the error to be handled by the caller
            raise e

        # Log
        self.__logger.info(
            f"Serial console port and data port opened with baudrate {self.__baudrate}."
        )

    @final
    def is_open(self) -> bool:
        with (self.__rlock):
            return not self.__stop_event.is_set() and self.__opened_event.is_set()

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
            f"Received message: {first_line}"
        ) if self.__debug else None

        # If the server is set, send the message to the server
        self.__server_dispatcher.broadcast_serial_incoming_message(
            msg_str
        ) if self.__server_dispatcher else None

    @final
    def _get_outgoing_message(self) -> OutgoingMessage | None:
        try:
            # Get the message from the queue
            msg = self.__outgoing_messages_queue.get(
                timeout=self.OUTGOING_WAIT_TIMEOUT
            )

        except Empty:
            # If the queue is empty, return None
            return None

        # Log
        first_line = str(msg).split('\n')[0]
        self.__logger.debug(
            f"Sending message: {first_line}"
        ) if self.__debug else None

        # If the server is set, send the message to the server
        self.__server_dispatcher.broadcast_serial_outgoing_message(
            first_line
        ) if self.__server_dispatcher else None

        return msg

    @final
    def _send_confirmation_message(self) -> None:
        self.__outgoing_messages_queue.put(OutgoingMessage(OutgoingCategory.STATUS, Status.OK))

    @final
    def _wait_confirmation_message(
        self,
        msg_to_confirm: OutgoingMessage
    ) -> None:
        # Log
        self.__logger.debug(
            f"Waiting for confirmation message for: {msg_to_confirm}"
        ) if self.__debug else None

        # Wait for the confirmation message
        attempts = 0
        while attempts < self.CONFIRMATION_ATTEMPTS:
            if self.__console_serial.in_waiting == 0:
                attempts += 1
                sleep(self.INCOMING_DELAY)
                continue

            msg_str = self.__console_serial.readline().decode(ENCODE).strip()
            msg = IncomingMessage.from_string(msg_str)

            if msg.is_confirmation():
                # Log the confirmation message
                self.__logger.debug(
                    f"Received confirmation message: {msg.content}"
                ) if self.__debug else None
                return

            elif msg.is_error():
                raise RuntimeError(
                    f"Received error message: {msg.content}"
                )

        raise RuntimeError(
            f"Confirmation message for {msg_to_confirm} not received within timeout."
        )

    @final
    def _send_stop_message(self) -> None:
        self.__outgoing_messages_queue.put(OutgoingMessage(OutgoingCategory.STATUS, Status.STOP))

        # Wait for the confirmation message
        self._wait_confirmation_message()

    @final
    def _receiving_message_handler(self) -> None:
        # Log
        self.__logger.info(
            f"Serial port receiving handler started for port {self.__console_port}."
        )

        # Check if there is an initialization message received
        while self.is_open():
            if self.__console_serial.in_waiting > 0:
                console_msg = self.__console_serial.read(
                    self.__console_serial.in_waiting
                ).decode(ENCODE).strip()
                self.__logger.debug(
                    "Received initialization message: " + console_msg
                ) if self.__debug else None

                # Get the Message from the string
                msg = IncomingMessage.from_string(console_msg)

                # Check if the message is a start message
                if msg.is_start():
                    # Check if the challenge is set
                    if not Env.has_challenge():
                        # Send the stop message
                        self._send_stop_message()

                        # Stop the communication
                        self.__stop_event()

                        # Log
                        self.__logger.warning(
                            "Challenge not set. Stopping communication."
                        )
                        return

                    # Send a confirmation message
                    self._send_confirmation_message()

                    # Set the start event
                    self.__start_event.set()

                    # Log
                    self.__logger.info(
                        "Received start event."
                    )
                    break

                elif msg.is_challenge():
                    # Send a confirmation message
                    self._send_confirmation_message()

                    # Set the challenge as an environment variable
                    Env.set_challenge(Challenge.from_string(msg.content))

                    # Log
                    self.__logger.info(
                        "Received challenge message."
                    )
                    # Continue to wait for the start event
                    continue

                elif msg.is_error():
                    # Log
                    self.__logger.error(
                        f"Received error message: {msg.content}"
                    )

                    raise RuntimeError(
                        f"Received error message: {msg.content}"
                    )

        while self.is_open():
            if self.__console_serial.in_waiting == 0:
                sleep(self.INCOMING_DELAY)
                continue

            # Parse the message from the serial port
            msg_str = self.__console_serial.readline().decode(ENCODE).strip()
            msg = IncomingMessage.from_string(msg_str)

            if msg.is_bno08x_yaw():
                # Log
                self.__logger.debug(
                    f"Received BNO08X yaw message: {msg.content}"
                ) if self.__debug else None

                # Update the BNO08X yaw angle
                with self.__bno08x_yaw_deg.get_lock():
                    self.__bno08x_yaw_deg.value = float(msg.content)

            elif msg.is_bno08x_turns():
                # Log
                self.__logger.debug(
                    f"Received BNO08X turns message: {msg.content}"
                ) if self.__debug else None

                # Update the BNO08X turns
                with self.__bno08x_turns.get_lock():
                    self.__bno08x_turns.value = int(msg.content)

            elif msg.is_error():
                # Log
                self.__logger.error(
                    f"Received error message: {msg.content}"
                )

                raise RuntimeError(
                    f"Received error message: {msg.content}"
                )

            # Put the message in the incoming messages queue
            self._put_incoming_message(msg)

        # Close the console serial port
        if self.__console_serial and self.__console_serial.is_open:
            self.__console_serial.close()
            self.__console_serial = None

        # Log
        self.__logger.info(
            f"Serial port receiving handler stopped for port {self.__console_port}."
        )

    @final
    def _sending_message_handler(self) -> None:
        # Log 
        self.__logger.info(
            "Waiting for start event on receiving handler..."
        )

        # Wait for start event to be set
        self.__start_event.wait()

        # Log
        self.__logger.info(
            f"Serial port sending handler started for port {self.__data_port}."
        )

        while self.is_open():
            # Get the message from the queue
            msg = self._get_outgoing_message()
            if not msg:
                continue

            # Send the message to the serial port
            self.__data_serial.write(str(msg).encode(ENCODE))

            # Flush the serial port to ensure the message is sent
            self.__data_serial.flush()

        # Send the stop message to the serial port
        if self.__data_serial and self.__data_serial.is_open:
            self._send_stop_message()

        # Clear the start event
        self.__start_event.clear()

        # Close the data serial port
        if self.__data_serial and self.__data_serial.is_open:
            self.__data_serial.close()
            self.__data_serial = None

        # Log
        self.__logger.info(
            f"Serial port sending handler stopped for port {self.__data_port}."
        )

    @final
    @ignore_sigint
    @log_on_error()
    def run(self) -> None:
        with self.__rlock:
            # Check if the stop event is set
            if self.__stop_event.is_set():
                self.__logger.warning(
                    "Stop event is set. Serial communication will not run."
                )
                return

            # Check if the websocket server is already running
            if self.is_open():
                self.__logger.warning(
                    "Serial communication is already running. Cannot start again."
                )
                return

            # Set the opened event to signal that the websocket server is ready
            self.__opened_event.set()

        # Open the serial ports
        self._open()

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

        # Clear the opened event
        with self.__rlock:
            self.__opened_event.clear()

    def __del__(self):
        """
        Destructor to clean up resources when the SerialCommunication instance is deleted.
        """
        self.__stop_event.set()

        # Log
        self.__logger.debug(
            "SerialCommunication instance is being deleted. Resources will be cleaned up."
        )
