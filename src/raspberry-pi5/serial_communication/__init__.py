import time
from multiprocessing import Event, Queue, RLock
from multiprocessing.synchronize import Event as EventCls
from threading import Thread
from typing import Optional
from time import sleep

from serial import Serial, SerialException

from camera.images_queue import ImagesQueue
from log import Logger
from log.sub_logger import SubLogger
from serial_communication.message import Message
from server import RealtimeTrackerServer
from utils import check_type


class SerialCommunication:
    """
    Class to handle the serial communication with the Raspberry Pi Pico.
    """
    # Logger configuration
    LOG_TAG = "Serial"

    # Message delay
    DELAY = 0.01

    # Encode
    ENCODE = 'utf-8'

    def __init__(
        self,
        logger: Optional[Logger] = None,
        images_queue: Optional[ImagesQueue] = None,
        server: Optional[RealtimeTrackerServer] = None,
        port: str = '/dev/ttyACM0',
        baudrate: int = 115200
    ):
        """
        Initialize the serial communication class.

        Args:
            logger (Logger): Logger instance for logging messages.
            images_queue (ImagesQueue): Images queue for handling images.
            port (str): Serial port to use for communication. Default is '/dev/ttyACM0'.
            baudrate (int): Baud rate for the serial communication. Default is 115200.
            server (RealtimeTrackerServer): Server instance for sending messages to the server. Default is None.
        """
        # Create the reentrant lock
        self.__rlock = RLock()

        # Create the parking event
        self.__parking_event = Event()

        # Create the stop event
        self.__stop_event = Event()

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

        # Initialize the incoming and outgoing messages queues
        self.__incoming_messages_queue = None
        self.__outgoing_messages_queue = None

        # Initialize the last incoming message
        self.__last_incoming_message = None

        # Set the serial port and baud rate
        self.__port = port
        self.__baudrate = baudrate

        # Initialize the serial port
        self.__serial = None

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

    def __clear_events(self) -> None:
        """
        Clear the events.
        """
        with self.__rlock:
            # Clear the stop event
            self.__stop_event.clear()

            # Clear the capture image event
            if self.__capture_image_event:
                self.__capture_image_event.clear()

            # Clear the pending incoming and outgoing message event
            self.__pending_incoming_message_event.clear()
            self.__pending_outgoing_message_event.clear()

    def is_open(self) -> bool:
        """
        Check if the serial port is open.

        Returns:
            bool: True if the serial port is open, False otherwise.
        """
        with self.__rlock:
            return self.__serial and self.__serial.is_open

    def is_closed(self) -> bool:
        """
        Check if the serial port is closed.

        Returns:
            bool: True if the serial port is closed, False otherwise.
        """
        return not self.is_open()

    def __open(self) -> None:
        """
        Open the communication.
        """
        with self.__rlock:
            # Check if the serial port is already open
            if self.is_open():
                return

            # Clear the events
            self.__clear_events()

            # Clear the last incoming message
            self.__last_incoming_message = None

            # Create the incoming and outgoing messages queues
            self.__incoming_messages_queue = Queue()
            self.__outgoing_messages_queue = Queue()

            # Open the serial port
            try:
                self.__serial = Serial(self.__port, self.__baudrate)
            except SerialException as e:
                self.__log(f"Error opening serial port: {e}")
                return

        # Log
        self.__log(f"Serial port {self.__port} opened with baudrate {self.__baudrate}.")

    def __close(self) -> None:
        """
        Close the communication.
        """
        with self.__rlock:
            # Check if the serial port is already closed
            if self.is_closed():
                return

            # Clear the events
            self.__clear_events()

            # Clear the last incoming message
            self.__last_incoming_message = None

            # Close the queues
            self.__incoming_messages_queue.close()
            self.__outgoing_messages_queue.close()

            # Close the serial port
            self.__serial.close()

            # Log
            self.__log(f"Serial port {self.__port} closed.")

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
    
            # If the server is set, send the message to the server
            if self.__server:
                self.__server.send_serial_incoming_message(str(message))
    
            # Log
            self.__log(f"Received message: {message}")

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
        return self.__last_incoming_message

    def send_message(self, message: Message) -> None:
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

            print(f"Message sent: {message}")

            # Set the pending outgoing message event
            self.__pending_outgoing_message_event.set()

    def send_rplidar_measures(self, measures_str: str) -> None:
        """
        Put RPLIDAR measures in the outgoing messages queue.

        Args:
            measures_str (str): The measures string to put in the queue.
        """
        # Create a message with the RPLIDAR measures type
        message = Message(Message.TYPE_RPLIDAR_MEASURES, measures_str)

        # Put the message in the outgoing messages queue
        self.send_message(message)

    def __get_outgoing_message(self) -> str | None:
        """
        Get a message from the outgoing messages queue.

        Returns:
            str|None: The message from the outgoing messages queue or None if no message is available.
        """
        message = None
        if self.is_open():
            # Check if there is a pending outgoing message
            if not self.__pending_outgoing_message_event.is_set():
                return None

            # Get the message from the queue
            message = self.__outgoing_messages_queue.get()

            # Clear the pending outgoing message event
            if self.__outgoing_messages_queue.empty():
                self.__pending_outgoing_message_event.clear()

        # Log
        self.__log(f"Sending message: {message}")

        # If the server is set, send the message to the server
        if self.__server:
            self.__server.send_serial_outgoing_message(message)

        return message

    def __receiving_message_handler(self) -> None:
        """
        Handler to receive messages from the serial port.
        """
        while not self.__stop_event.is_set():
            # Check if there is a message to read
            if not self.__serial.in_waiting > 0:
                return None

            # Read the message from the serial port
            message_str = self.__serial.readline().decode(self.ENCODE).strip()

            # Split the message into type and content
            message_separator_idx = message_str.find(Message.HEADER_SEPARATOR)

            # Create the message object
            message = Message(
                message_str[:message_separator_idx],
                message_str[message_separator_idx + 1:],
            )

            # Put the message in the incoming messages queue
            self.__put_incoming_message(message)

            # Sleep for a short time to avoid busy waiting
            sleep(self.DELAY)

    def __sending_message_handler(self) -> None:
        """
        Handler to send messages to the serial port.
        """
        while not self.__stop_event.is_set():
            # Check if there is a message to send
            if not self.__pending_outgoing_message_event.is_set():
                return

            # Get the message from the queue
            message = self.__get_outgoing_message()

            # Send the message to the serial port
            self.__serial.write(str(message).encode(self.ENCODE))

            # Wait for the message to be sent
            sleep(self.DELAY)

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