import time
from multiprocessing import Event, Queue, RLock
from multiprocessing.synchronize import Event as EventCls
from threading import Thread
from typing import Optional
from time import sleep
import asyncio

from serial import Serial, SerialException

from camera.images_queue import ImagesQueue
from log import Logger
from log.sub_logger import SubLogger
from serial_communication.message import Message
from server import RealtimeTrackerServer
from utils import check_type
from env import Env

class SerialCommunication:
    """
    Class to handle the serial communication through USB.
    """
    # Logger configuration
    LOG_TAG = "Serial"

    # Raspberry Pi Pico baud rate
    RASPBERRY_PI_PICO_BAUDRATE = 115200

    # Raspberry PI Pico console port
    RASPBERRY_PI_PICO_CONSOLE_PORT = '/dev/ttyACM0'

    # Raspberry PI Pico data port
    RASPBERRY_PI_PICO_DATA_PORT = '/dev/ttyACM1'

    # Message delay
    DELAY = 0.01

    # Encode
    ENCODE = 'utf-8'

    # Types of messages
    TYPE_CAPTURE_IMAGE = 'capture_image'
    TYPE_INFERENCE = 'inference'
    TYPE_RPLIDAR = "rplidar"
    TYPE_DEBUG = 'debug'
    TYPE_STATUS = 'status'

    # Types of Status
    TYPE_STATUS_ON = 'on'
    TYPE_STATUS_OFF = 'off'

    def __init__(
        self,
        logger: Optional[Logger] = None,
        images_queue: Optional[ImagesQueue] = None,
        server: Optional[RealtimeTrackerServer] = None,
        data_port: Optional[str] = RASPBERRY_PI_PICO_DATA_PORT,
        console_port: Optional[str] = RASPBERRY_PI_PICO_CONSOLE_PORT,
        baudrate: Optional[int] = RASPBERRY_PI_PICO_BAUDRATE
    ):
        """
        Initialize the serial communication class.

        Args:
            logger (Logger): Logger instance for logging messages.
            images_queue (ImagesQueue): Images queue for handling images.
            data_port (str): Serial port used for sending data to Pico
            console_port (str): Serial port used for receiving data from Pico.
            baudrate (int): Baud rate for the serial communication. Default is 115200.
            server (RealtimeTrackerServer): Server instance for sending messages to the server. Default is None.
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
        if images_queue:
            check_type(images_queue, ImagesQueue)
        self.__images_queue = images_queue

        # Check the type of the server
        if server:
            check_type(server, RealtimeTrackerServer)
        self.__server = server

        # Check the type of the logger
        if logger:
            check_type(logger, Logger)

            # Get the sub-logger for this class
            self.__logger = SubLogger(logger, self.LOG_TAG)
        else:
            self.__logger = None

        # Get the capture image event
        if images_queue:
            self.__capture_image_event = self.__images_queue.get_capture_image_event()
        else:
            self.__capture_image_event = None

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

        # Set the serial port, alternative serial port and baud rate
        check_type(data_port, str)
        self.__data_port = data_port
        check_type(console_port, str)
        self.__console_port = console_port
        check_type(baudrate, int)
        self.__baudrate = baudrate

        # Initialize the console and data serial ports
        self.__console_serial = None
        self.__data_serial = None

        # Get the debug environment variable
        self.__debug = Env.get_debug_mode()

    def __log(self, message: str, log_to_file: bool = True, print_to_console: bool = True):
        """
        Logs a message using the logger if available.

        Args:
            message (str): The message to log.
            log_to_file (bool): Whether to log to file using the logger.
            print_to_console (bool): Whether to print the message to console.
        """
        if self.__logger and log_to_file:
            self.__logger.log(message)

        if print_to_console:
            print(f"{self.LOG_TAG}: {message}")

    def is_open(self) -> bool:
        """
        Check if the serial port is open.

        Returns:
            bool: True if the serial port is open, False otherwise.
        """
        with (self.__rlock):
            return not self.__stop_event.is_set() and self.__console_serial and self.__console_serial.is_open and self.__data_serial and self.__data_serial.is_open

    def is_closed(self) -> bool:
        """
        Check if the serial port is closed.

        Returns:
            bool: True if the serial port is closed, False otherwise.
        """
        return not self.is_open()

    def has_started(self) -> bool:
        """
        Check if the communication has started.

        Returns:
            bool: True if the communication has started, False otherwise.
        """
        with self.__rlock:
            return self.__start_event.is_set()

    def __open(self) -> None:
        """
        Open the communication.
        """
        with self.__rlock:
            # Check if the serial port is already open
            if self.is_open():
                return

            # Clear the stop event
            self.__stop_event.clear()

            # Clear the capture image event
            if self.__capture_image_event:
                self.__capture_image_event.clear()

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

            # Open the data and console ports
            try:
                self.__console_serial = Serial(self.__console_port, self.__baudrate)

            except SerialException as e:
                raise RuntimeError(f"Error opening serial console port: {e}")
            
            try:
                self.__data_serial = Serial(self.__data_port, self.__baudrate)

            except SerialException as alt_e:
                raise RuntimeError(f"Error opening serial data port: {alt_e}")

        # Log
        self.__log(f"Serial console port '{self.__console_port}' and data port '{self.__data_port}' opened with baudrate {self.__baudrate}.")

    def __close(self) -> None:
        """
        Close the communication.
        """
        with self.__rlock:
            # Check if the serial port is already closed
            if self.is_closed():
                return

            # Clear the stop event
            self.__stop_event.set()

            # Clear the capture image event
            if self.__capture_image_event:
                self.__capture_image_event.clear()

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
        self.__log(f"Serial console port '{self.__console_port}' and data port '{self.__data_port}' closed.")

    def __put_incoming_message(self, message: Message) -> None:
        """
        Put a message in the incoming messages queue.

        Args:
            message (Message): The message to put in the queue.
        """
        with self.__rlock:
            if self.is_closed():
                return
                
            # Put the message in the queue
            self.__outgoing_messages_queue.put(message)
    
            # Set the last incoming message
            self.__last_incoming_message = message
    
            # Set the pending incoming message event
            self.__pending_incoming_message_event.set()
    
        # Log
        first_line = str(message).split('\n')[0]
        self.__log(f"Received message: {first_line}", print_to_console=self.__debug)

        # If the server is set, send the message to the server
        if self.__server:
            self.__server.send_serial_incoming_message(str(message))

    def receive_message(self) -> Message | None:
        """
        Get a message from the incoming messages queue.

        Returns:
            Message|None: The message from the incoming messages queue or None if no message is available.
        """
        with self.__rlock:
            if self.is_closed():
                return None

            # Check if there is a pending incoming message
            if not self.__pending_incoming_message_event.is_set():
                return None

            # Get the message from the queue
            message = self.__incoming_messages_queue.get()

            # Clear the pending incoming message event
            if self.__incoming_messages_queue.empty():
                self.__pending_incoming_message_event.clear()

            return message

    def peek_last_received_message(self) -> Message | None:
        """
        Peek the last message from the incoming messages queue without removing it.

        Returns:
            Message|None: The last incoming message or None if no message is available.
        """
        with self.__rlock:
            return self.__last_incoming_message

    def _send_message(self, message: Message) -> None:
        """
        Put a message in the outgoing messages queue.

        Args:
            message (Message): The message to put in the queue.
        """
        # Check the type of message
        check_type(message, Message)

        with self.__rlock:
            if self.is_closed():
                return

            # Put the message in the queue
            self.__outgoing_messages_queue.put(message)

            # Set the pending outgoing message event
            self.__pending_outgoing_message_event.set()

        # Log
        # self.__log(f"Sending message: {message}", print_to_console=False)

    def send_rplidar_measures(self, measures_str: str) -> None:
        """
        Put RPLIDAR measures in the outgoing messages queue.

        Args:
            measures_str (str): The measures string to put in the queue.
        """
        # Create a message with the RPLIDAR measures type
        message = Message(self.TYPE_RPLIDAR, measures_str)

        # Put the message in the outgoing messages queue
        self._send_message(message)

    def __get_outgoing_message(self) -> str | None:
        """
        Get a message from the outgoing messages queue.

        Returns:
            str|None: The message from the outgoing messages queue or None if no message is available.
        """
        with self.__rlock:
            message = None
            if not self.is_open():
                return None
            
            # Check if there is a pending outgoing message
            if not self.__pending_outgoing_message_event.is_set():
                return None
                
            # Check if the queue is closed or empty
            if self.__queues_closed_event.is_set() or self.__outgoing_messages_queue.empty():
                return None

            # Get the message from the queue
            message = self.__outgoing_messages_queue.get()

            # Clear the pending outgoing message event
            if self.__outgoing_messages_queue.empty():
                self.__pending_outgoing_message_event.clear()

        # Log
        message_str = str(message)
        first_line = message_str.split('\n')[0]
        self.__log(f"Sending message: {first_line}", print_to_console=self.__debug)

        # If the server is set, send the message to the server
        if self.__server:
            asyncio.run(self.__server.broadcast_serial_outgoing_message(message_str))

        return message

    def __receiving_message_handler(self) -> None:
        """
        Handler to receive messages from the serial port.
        """
        # Log
        self.__log(f"Serial port receiving handler started for port {self.__console_port}.")

        # Check if there is a initialization message received
        while True:
            if self.is_open() and self.__console_serial.in_waiting > 0:
                data = self.__console_serial.read(self.__console_serial.in_waiting).decode(self.ENCODE).strip()
                self.__log("Received initialization message: " + data)

                # Check if it's a start message
                parts = data.split(Message.HEADER_SEPARATOR)
                if len(parts) < 2:
                    continue

                if parts[0] == self.TYPE_STATUS and parts[1] == self.TYPE_STATUS_ON:
                   # Set the start event
                    self.__start_event.set()

                    # Log
                    self.__log("Received start event.")
                    break

                """
                # Read the initialization message
                self.__log(f"Initialization message received: {data}")
                self.__console_serial.reset_input_buffer()
                self.__console_serial.reset_output_buffer()
                self.__log("Input and output buffers reset.")
                """
        
        while self.is_open():
            if not self.__console_serial.in_waiting > 0:
                sleep(self.DELAY)
                continue

            message_str = self.__console_serial.readline().decode(self.ENCODE).strip()

            # Split the message into type and content
            message_parts = message_str.split(Message.HEADER_SEPARATOR)
            if len(message_parts) < 2:
                continue

            if message_parts[0] == self.TYPE_STATUS:
                if message_parts[1] == self.TYPE_STATUS_OFF:
                    # Set the stop event
                    self.__stop_event.set()
                    break
                else:
                    self.__log("Received status message: " + message_str)

            # Create the message object
            message = Message(
                message_parts[0],
                message_parts[1],
            )

            # Put the message in the incoming messages queue
            #self.__log("Received message: " +str(message))
            self.__put_incoming_message(message)

            # Sleep for a short time to avoid busy waiting
            sleep(self.DELAY)

        self.__log(f"Serial port receiving handler stopped for port {self.__console_port}.")

    def __sending_message_handler(self) -> None:
        """
        Handler to send messages to the serial port.
        """
        # Log 
        self.__log("Waiting for start event on receiving handler...")

        # Wait for start event to be set
        self.__start_event.wait()

        # Log
        self.__log(f"Serial port sending handler started for port {self.__data_port}.")

        while self.is_open():
            # Check if there is a message to send
            self.__pending_outgoing_message_event.wait()

            # Get the message from the queue
            message = self.__get_outgoing_message()
            if not message:
                # If there is no message, wait for a short time
                sleep(self.DELAY)
                continue

            # Send the message to the serial port
            #print(f"Sending message: {str(message).encode(self.ENCODE)}")
            self.__data_serial.write(str(message).encode(self.ENCODE))

            # Wait for the message to be sent
            # sleep(self.DELAY)

        self.__log(f"Serial port sending handler stopped for port {self.__data_port}.")

    def __create_sending_thread(self) -> None:
        """
        Create a thread to handle sending messages.
        """
        with self.__rlock:
            self.__open()
            thread = Thread(target=self.__sending_message_handler)
            thread.start()

    def __create_receiving_thread(self) -> None:
        """
        Create a thread to handle receiving messages.
        """
        with self.__rlock:
            self.__open()
            thread = Thread(target=self.__receiving_message_handler)
            thread.start()

    def create_threads(self) -> None:
        """
        Create threads for receiving and sending messages.
        """
        with self.__rlock:
            # Create the receiving thread
            self.__create_receiving_thread()

            # Create the sending thread
            self.__create_sending_thread()

            # Log
            self.__log("Communication threads created.")

    def start_threads(self) -> None:
        """
        Start the communication threads.
        """
        with self.__rlock:
            # Set the start event
            self.__start_event.set()

            # Log
            self.__log("Communication threads started.")

    def stop_threads(self) -> None:
        """
        Stop the communication threads.
        """
        with self.__rlock:
            # Close the serial port
            self.__close()

    def get_stop_event(self) -> EventCls:
        """
        Get the stop event status.

        Returns:
            Event: The event that indicates when to stop the communication.
        """
        return self.__stop_event
    
    def get_start_event(self) -> EventCls:
        """
        Get the start event status.

        Returns:
            Event: The event that indicates when to start the communication.
        """
        return self.__start_event
    
    def get_parking_event(self) -> EventCls:
        """
        Get the parking event status.

        Returns:
            Event: The event that indicates when to park.
        """
        return self.__parking_event

    def get_pending_incoming_message_event(self) -> EventCls:
        """
        Get the pending incoming message event status.

        Returns:
            Event: The event that indicates when there is a pending incoming message.
        """
        return self.__pending_incoming_message_event

    def get_pending_outgoing_message_event(self) -> EventCls:
        """
        Get the pending outgoing message event status.

        Returns:
            Event: The event that indicates when there is a pending outgoing message.
        """
        return self.__pending_outgoing_message_event                

    def __del__(self):
        """
        Destructor for the serial communication.
        """
        self.stop_threads()