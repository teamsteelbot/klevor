from multiprocessing import Event, Queue, RLock
from threading import Thread
from typing import Optional, final
from time import sleep
import asyncio

from serial import Serial, SerialException

from ..camera.image_processing_queue import ImageProcessingQueue
from ..log import Logger
from ..log.sub_logger import SubLogger
from .message import IncomingMessage, IncomingCategory, OutgoingMessage, OutgoingCategory, Status, RPLIDAR
from .abstracts import SerialCommunicationABC
from ..server import WebsocketsServerABC
from ..utils import check_type
from ..env import Env, Challenge

class SerialCommunication(SerialCommunicationABC):
    """
    Class to handle the serial communication through USB.
    """

    # Logger configuration
    LOG_TAG = "Serial"

    # Raspberry Pi Pico baud rate
    RASPBERRY_PI_PICO_BAUDRATE = 115200

    # Raspberry PI Pico console port
    RASPBERRY_PI_PICO_CONSOLE_PORT = '/dev/ttyACM0'
    RASPBERRY_PI_PICO_CONSOLE_PORT_ALT = '/dev/ttyACM2'

    # Raspberry PI Pico data port
    RASPBERRY_PI_PICO_DATA_PORT = '/dev/ttyACM1'
    RASPBERRY_PI_PICO_DATA_PORT_ALT = '/dev/ttyACM3'

    # Message delay
    DELAY = 0.01

    # Stop delay
    STOP_DELAY = 0.1

    # Encode
    ENCODE = 'utf-8'

    def __init__(
        self,
        logger: Optional[Logger] = None,
        images_queue: Optional[ImageProcessingQueue] = None,
        server: Optional[WebsocketsServerABC] = None,
        console_port: Optional[str] = RASPBERRY_PI_PICO_CONSOLE_PORT,
        console_port_alt: Optional[str] = RASPBERRY_PI_PICO_CONSOLE_PORT_ALT,
        data_port: Optional[str] = RASPBERRY_PI_PICO_DATA_PORT,
        data_port_alt: Optional[str] = RASPBERRY_PI_PICO_DATA_PORT_ALT,
        baudrate: Optional[int] = RASPBERRY_PI_PICO_BAUDRATE
    ):
        """
        Initialize the serial communication class.

        Args:
            logger (Optional[Logger]): Logger instance for logging messages.
            images_queue (Optional[ImageProcessingQueue]): Images queue for handling images.
            console_port (Optional[str]): Serial port used for receiving data from Pico.
            console_port_alt (Optional[str]): Alternative serial port used for receiving data from Pico.
            data_port (Optional[str]): Serial port used for sending data to Pico.
            data_port_alt (Optional[str]): Alternative serial port used for sending data to Pico.
            baudrate (Optional[int]): Baud rate for the serial communication. Default is 115200.
            server (Optional[WebsocketsServerABC]): Server instance for sending messages to the server. Default is None.
        """
        # Create the reentrant lock
        self.__rlock = RLock()

        # Create the parking event
        self.__parking_event = Event()

        # Create the stop event
        self.__stop_event = Event()

        # Create the start event
        self.__start_event = Event()

        # Check the type of images queue
        check_type(images_queue, ImageProcessingQueue) if images_queue else None
        self.__images_queue = images_queue

        # Check the type of the server
        check_type(server, WebsocketsServerABC) if server else None
        self.__server = server

        # Check the type of the logger
        check_type(logger, Logger) if logger else None

        # Get the sub-logger for this class
        self.__logger = SubLogger(logger, self.LOG_TAG) if logger else None

        # Create the pending incoming and outgoing message event
        self.__pending_incoming_message_event = Event()
        self.__pending_outgoing_message_event = Event()

        # Create the queues closed event
        self.__queues_closed_event = Event()

        # Initialize the incoming and outgoing messages queues
        self.__incoming_messages_queue = None
        self.__outgoing_messages_queue = None

        # Initialize the last incoming message
        self.__last_incoming_message = None

        # Check the type of console port and its alternative port
        check_type(console_port, str)
        self.__console_port = console_port
        check_type(console_port_alt, str)
        self.__console_port_alt = console_port_alt

        # Check the type of data port and its alternative port
        check_type(data_port, str)
        self.__data_port = data_port
        check_type(data_port_alt, str)
        self.__data_port_alt = data_port_alt

        # Check the type of baudrate
        check_type(baudrate, int)
        self.__baudrate = baudrate

        # Initialize the console and data serial ports
        self.__console_serial = None
        self.__data_serial = None

        # Initialize the threads
        self.__receiving_thread = None
        self.__sending_thread = None

        # Get the debug environment variable
        self.__debug = Env.get_debug_mode()

    def __open(self) -> None:
        """
        Open the communication.
        """
        with self.__rlock:
            # Clear the stop event
            self.__stop_event.clear()

            # Clear the pending incoming and outgoing message event
            self.__pending_incoming_message_event.clear()
            self.__pending_outgoing_message_event.clear()

            # Clear the start event
            self.__start_event.clear()

            # Clear the last incoming message
            self.__last_incoming_message = None

            # Create the incoming and outgoing messages queues
            self.__incoming_messages_queue = Queue()
            self.__outgoing_messages_queue = Queue()

            # Clear queues closed event
            self.__queues_closed_event.clear()

            # Open the console port
            try:
                self.__console_serial = Serial(self.__console_port, self.__baudrate)

            except SerialException as port_e:
                # Try its alternative port
                try:
                    self.__console_serial = Serial(self.__console_port_alt, self.__baudrate)

                except SerialException as port_alt_e:
                    raise RuntimeError(f"Error opening serial console port: {port_e} and alternative port: {port_alt_e}")

                raise RuntimeError(f"Error opening serial console port: {port_e}")

            # Open the data port
            try:
                self.__data_serial = Serial(self.__data_port, self.__baudrate)

            except SerialException as port_e:
                # Try its alternative port
                try:
                    self.__data_serial = Serial(self.__data_port_alt, self.__baudrate)

                except SerialException as port_alt_e:
                    raise RuntimeError(f"Error opening serial data port: {port_e} and alternative port: {port_alt_e}")

                raise RuntimeError(f"Error opening serial data port: {port_e}")

        # Log
        self.__logger.info(
            f"Serial console port and data port opened with baudrate {self.__baudrate}.") if self.__logger else None

    @final
    def is_open(self) -> bool:
        with (self.__rlock):
            return not self.__stop_event.is_set() and self.__console_serial and self.__console_serial.is_open and self.__data_serial and self.__data_serial.is_open

    def __close(self) -> None:
        """
        Close the communication.
        """
        with self.__rlock:
            # Clear the stop event
            self.__stop_event.set()

            # Clear the pending incoming message event
            self.__pending_incoming_message_event.set()

            # Set the pending outgoing message event to ensure no messages are left to send
            self.__pending_outgoing_message_event.set()

            # Set the start event
            self.__start_event.set()

            # Clear the last incoming message
            self.__last_incoming_message = None

            # Close the queues
            self.__incoming_messages_queue.close()
            self.__outgoing_messages_queue.close()

            # Set the queues closed event
            self.__queues_closed_event.set()

        # Log
        self.__logger.info(f"Serial console port '{self.__console_port}' and data port '{self.__data_port}' closed.") if self.__logger else None

    @final
    def is_closed(self) -> bool:
        return not self.is_open()
    
    @final 
    def start(self) -> None:
        with self.__rlock:
            self.__start_event.set()

    @final
    def has_started(self) -> bool:
        with self.__rlock:
            return self.__start_event.is_set()

    def __put_incoming_message(self, msg: IncomingMessage) -> None:
        """
        Put a message in the incoming messages queue.

        Args:
            msg (IncomingMessage): The message to put in the queue.
        """
        with self.__rlock:
            # Put the message in the queue
            self.__outgoing_messages_queue.put(msg)
    
            # Set the last incoming message
            self.__last_incoming_message = msg
    
            # Set the pending incoming message event
            self.__pending_incoming_message_event.set()
    
        # Log
        msg_str = str(msg)
        first_line = str(msg).split('\n')[0]
        self.__logger.debug(f"Received message: {first_line}") if self.__logger and self.__debug else None

        # If the server is set, send the message to the server
        asyncio.run(self.__server.broadcast_serial_incoming_message(msg_str)) if self.__server else None

    @final
    def receive_message(self) -> IncomingMessage | None:
        with self.__rlock:
            if self.is_closed() or not self.__pending_incoming_message_event.is_set():
                return None

            # Check if the queue is closed or empty
            if self.__queues_closed_event.is_set() or self.__incoming_messages_queue.empty():
                    return None

            # Get the message from the queue
            msg = self.__incoming_messages_queue.get()

            # Clear the pending incoming message event
            if self.__incoming_messages_queue.empty():
                self.__pending_incoming_message_event.clear()

            return msg

    @final
    def peek_last_received_message(self) -> OutgoingMessage | None:
        with self.__rlock:
            return self.__last_incoming_message

    def __get_outgoing_message(self) -> str | None:
        """
        Get a message from the outgoing messages queue.

        Returns:
            str|None: The message from the outgoing messages queue or None if no message is available.
        """
        with self.__rlock:
            if self.is_closed() or not self.__pending_outgoing_message_event.is_set():
                return None
                
            # Check if the queue is closed or empty
            if self.__queues_closed_event.is_set() or self.__outgoing_messages_queue.empty():
                return None

            # Get the message from the queue
            msg = self.__outgoing_messages_queue.get()

            # Clear the pending outgoing message event
            if self.__outgoing_messages_queue.empty():
                self.__pending_outgoing_message_event.clear()

        # Log
        msg_str = str(msg)
        first_line = msg_str.split('\n')[0]
        self.__logger.debug(f"Sending message: {first_line}") if self.__logger and self.__debug else None

        # If the server is set, send the message to the server
        asyncio.run(self.__server.broadcast_serial_outgoing_message(msg_str)) if self.__server else None

        return msg

    @final
    def _send_message(self, msg: OutgoingMessage) -> None:
        # Check the type of message
        check_type(msg, OutgoingMessage)

        with self.__rlock:
            if self.is_closed():
                return

            # Put the message in the queue
            self.__outgoing_messages_queue.put(msg)

            # Set the pending outgoing message event
            self.__pending_outgoing_message_event.set()

        # Log
        self.__logger.debug(f"Sending message: {message}") if self.__logger and self.__debug else None

    def _send_confirmation_message(self) -> None:
        """
        Send a confirmation message to the console port.
        """
        # Create a confirmation message
        confirmation_msg = OutgoingMessage(OutgoingCategory.STATUS, Status.OK)

        # Put the message in the outgoing messages queue
        self._send_message(confirmation_msg)

    @final
    def send_rplidar_measures(self, measures: dict[RPLIDAR, float]) -> None:
        for key, value in measures.items():
            # Check the type of key and value
            check_type(key, RPLIDAR)
            check_type(value, float)

            # Create a message with the RPLIDAR measures type
            msg = OutgoingMessage(OutgoingCategory.RPLIDAR, f"{key.get_name()}{OutgoingMessage.CONTENT_HEADER_SEPARATOR}{value}")

            # Put the message in the outgoing messages queue
            self._send_message(msg)

    @final
    def _receiving_message_handler(self) -> None:
        # Log
        self.__logger.info(f"Serial port receiving handler started for port {self.__console_port}.") if self.__logger else None

        # Check if there is an initialization message received
        while True:
            if self.is_open() and self.__console_serial.in_waiting > 0:
                console_msg = self.__console_serial.read(self.__console_serial.in_waiting).decode(self.ENCODE).strip()
                self.__logger.debug("Received initialization message: " + console_msg) if self.__logger and self.__debug else None

                # Get the Message from the string
                msg = IncomingMessage.from_string(console_msg)

                # Check if the message is a start message
                if msg.is_start():
                    # Set the start event
                    self.start()

                    # Log
                    self.__logger.info("Received start event.") if self.__logger else None

                    # Send a confirmation start message
                    self._send_confirmation_message()
                    break

                elif msg.is_challenge():
                    # Set the challenge as an environment variable
                    Env.set_challenge(Challenge.from_string(msg.content))

                    # Log
                    self.__logger.info("Received challenge message.") if self.__logger else None

                    # Send a challenge message
                    self._send_confirmation_message()

                    # Continue to wait for the start event
                    continue
        
        while self.is_open():
            if self.__console_serial.in_waiting == 0:
                sleep(self.DELAY)
                continue

            # Parse the message from the serial port
            msg_str = self.__console_serial.readline().decode(self.ENCODE).strip()
            msg = IncomingMessage.from_string(msg_str)

            if msg.is_stop():
                # Send a confirmation stop message
                self._send_confirmation_message()

                # Log the stop message
                self.__logger.info("Received stop event.") if self.__logger else None

                # Wait for a short time to ensure the message is sent
                sleep(self.STOP_DELAY)

                # Close the serial port
                self.__close()

            elif msg.is_error():
                # Log the error message
                self.__logger.error(f"Received error message: {msg.content}") if self.__logger else None

            else:
                # Log
                self.__logger.debug(f"Received message: {msg}") if self.__logger and self.__debug else None

            # Put the message in the incoming messages queue
            self.__put_incoming_message(msg)

        self.__logger.info(f"Serial port receiving handler stopped for port {self.__console_port}.") if self.__logger else None

    @final
    def _sending_message_handler(self) -> None:
        # Log 
        self.__logger.info("Waiting for start event on receiving handler...") if self.__logger else None

        # Wait for start event to be set
        self.__start_event.wait()

        # Log
        self.__logger.info(f"Serial port sending handler started for port {self.__data_port}.") if self.__logger else None

        while self.is_open():
            # Check if there is a message to send
            self.__pending_outgoing_message_event.wait()

            # Get the message from the queue
            msg = self.__get_outgoing_message()
            if not msg:
                # If there is no message, wait for a short time
                sleep(self.DELAY)
                continue

            # Send the message to the serial port
            self.__data_serial.write(str(msg).encode(self.ENCODE))

        self.__logger.info(f"Serial port sending handler stopped for port {self.__data_port}.") if self.__logger else None

    def create_threads(self) -> None:
        """
        Create threads for receiving and sending messages.
        """
        with self.__rlock:
            if self.is_open():
                self.__logger.warning("Communication threads already created.") if self.__logger else None
                return
            
            # Open the serial ports
            self.__open()
            
            # Create the receiving thread
            self.__receiving_thread = Thread(target=self._receiving_message_handler)
            self.__receiving_thread.start()
            
            # Create the sending thread
            self.__sending_thread = Thread(target=self._sending_message_handler)
            self.__sending_thread.start()

        # Log
        self.__logger.info("Communication threads created.") if self.__logger else None

    def stop_threads(self) -> None:
        """
        Stop the communication threads.
        """
        with self.__rlock:
            if self.is_closed():
                self.__logger.warning("Communication threads already stopped.") if self.__logger else None
                return
            
            # Close the serial port
            self.__close()
            
            # Wait for the receiving thread to finish
            if self.__receiving_thread:
                self.__receiving_thread.join()
                self.__receiving_thread = None
                
            # Wait for the sending thread to finish
            if self.__sending_thread:
                self.__sending_thread.join()
                self.__sending_thread = None

    @final
    def wait_stop_event(self) -> None:
        return self.__stop_event.wait()
    
    @final
    def wait_start_event(self) -> None:
        return self.__start_event.wait()
    
    @final
    def wait_parking_event(self) -> None:
        return self.__parking_event.wait()

    @final
    def wait_pending_incoming_message_event(self) -> None:
        return self.__pending_incoming_message_event.wait()

    @final
    def wait_pending_outgoing_message_event(self) -> None:
        return self.__pending_outgoing_message_event.wait()                

    def __del__(self):
        """
        Destructor for the serial communication.
        """
        self.stop_threads() if self.__receiving_thread or self.__sending_thread else None
        self.__close() if self.is_open() else None
        self.__logger.info("SerialCommunication instance deleted.") if self.__logger else None