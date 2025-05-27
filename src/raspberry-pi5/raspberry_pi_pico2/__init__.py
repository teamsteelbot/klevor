from multiprocessing import Event, Queue, Lock
from threading import Thread

import serial
import time

from camera.images_queue import ImagesQueue
from log import Logger
from server import RealtimeTrackerServer

# Message delay
MESSAGE_DELAY = 0.01

# Types of messages
MESSAGE_TYPE_CAPTURE_IMAGE = 'capture_image'
MESSAGE_TYPE_INFERENCE = 'inference'
MESSAGE_TYPES = [MESSAGE_TYPE_INFERENCE, MESSAGE_TYPE_CAPTURE_IMAGE]

# Message header separator
MESSAGE_HEADER_SEPARATOR = ':'

# Message end character
MESSAGE_END = '\n'

# Encode
ENCODE='utf-8'

class Message:
    """
    Class to handle the messages sent and received from the Raspberry Pi Pico.
    """
    __type = None
    __content = None

    def __init__(self, message_type: str, message_content: str):
        """
        Initialize the message class.

        Args:
            message_type (str): The type of the message. Must be one of MESSAGE_TYPES.
            message_content (str): The content of the message.
        """
        # Check if the message type is valid
        if message_type not in MESSAGE_TYPES:
            raise ValueError(f"Invalid message type: {message_type}")
        self.__type = message_type

        # Set the message content
        self.__content = message_content

    def __str__(self) -> str:
        """
        String representation of the message.
        """
        return f"{self.__type}{MESSAGE_HEADER_SEPARATOR}{self.__content}{MESSAGE_END}"

    def get_type(self) -> str:
        """
        Get the message type.

        Returns:
            str: The type of the message.
        """
        return self.__type

    def get_content(self) -> str:
        """
        Get the message content.

        Returns:
            str: The content of the message.
        """
        return self.__content

class SerialCommunication:
    """
    Class to handle the serial communication with the Raspberry Pi Pico.
    """
    __lock = None
    __log_tag = "SerialCommunication"
    __serial = None
    __parking_event = None
    __stop_event = None
    __logger = None
    __images_queue = None
    __port = None
    __baudrate = None
    __incoming_messages_queue = None
    __pending_incoming_message_event = None
    __outgoing_messages_queue = None
    __pending_outgoing_message_event = None
    __last_incoming_message = None
    __server = None

    def __init__(self, parking_event: Event, stop_event: Event, logger: Logger, images_queue: ImagesQueue, port='/dev/ttyACM0', baudrate=115200, server: RealtimeTrackerServer=None):
        """
        Initialize the serial communication class.
        """
        # Create the lock
        self.__lock = Lock()

        # Check the type of the parking event
        if not isinstance(parking_event, Event):
            raise ValueError("parking_event must be an instance of Event")
        self.__parking_event = parking_event

        # Check the type of the stop event
        if not isinstance(stop_event, Event):
            raise ValueError("stop_event must be an instance of Event")
        self.__stop_event = stop_event

        # Check the type of the images queue
        if not isinstance(images_queue, ImagesQueue):
            raise ValueError("images_queue must be an instance of ImagesQueue")
        self.__images_queue = images_queue

        # Check the type of the logger
        if not isinstance(logger, Logger):
            raise ValueError("logger must be an instance of Logger")

        # Get the sub-logger for this class
        self.__logger = logger.get_sub_logger(self.__log_tag)

        # Get the capture image event
        self.__capture_image_event = self.__images_queue.get_capture_image_event()

        # Create the pending incoming and outgoing message event
        self.__pending_incoming_message_event = Event()
        self.__pending_outgoing_message_event = Event()

        # Create the last incoming message
        self.__last_incoming_message = None

        # Set the serial port and baud rate
        self.__port = port
        self.__baudrate = baudrate

        # Set the server
        if server is not None and isinstance(server, RealtimeTrackerServer):
            self.__server = server

    def __clear_events(self)->None:
        """
        Clear the events.
        """
        # Clear the stop event
        self.__stop_event.clear()

        # Clear the capture image event
        self.__capture_image_event.clear()

        # Clear the pending incoming and outgoing message event
        self.__pending_incoming_message_event.clear()
        self.__pending_outgoing_message_event.clear()

    def __is_open(self) -> bool:
        """
        Check if the serial port is open.

        Returns:
            bool: True if the serial port is open, False otherwise.
        """
        return self.__serial is not None and self.__serial.is_open

    def start(self)->None:
        """
        Start the communication.
        """
        with self.__lock:
            # Check if the serial port is already open
            if self.__is_open():
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
                self.__serial = serial.Serial(self.__port, self.__baudrate)
            except serial.SerialException as e:
                self.__logger.log(f"Error opening serial port: {e}")
                return

        # Log
        self.__logger.log(f"Serial port {self.__port} opened with baudrate {self.__baudrate}.")

    def close(self)->None:
        """
        Close the communication.
        """
        with self.__lock:
            # Check if the serial port is already closed
            if not self.__is_open():
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
        self.__logger.log(f"Serial port {self.__port} closed.")

    def __put_incoming_message(self, message: Message)->None:
        """
        Put a message in the incoming messages queue.

        Args:
            message (Message): The message to put in the queue.
        """
        if self.__is_open():
            # Put the message in the queue
            self.__outgoing_messages_queue.put(message)

            # Set the last incoming message
            self.__last_incoming_message = message

            # Set the pending incoming message event
            self.__pending_incoming_message_event.set()

        # If the server is set, send the message to the server
        if self.__server is not None:
            self.__server.send_serial_incoming_message(str(message))

        # Log
        self.__logger.log(f"Received message: {message}")

    def get_incoming_message(self) -> Message|None:
        """
        Get a message from the incoming messages queue.

        Returns:
            Message|None: The message from the incoming messages queue or None if no message is available.
        """
        with self.__lock:
            if not self.__is_open():
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

    def peek_incoming_message(self) -> Message|None:
        """
        Peek a message from the incoming messages queue without removing it.

        Returns:
            Message|None: The last incoming message or None if no message is available.
        """
        with self.__lock:
            if not self.__is_open():
                return None

            return self.__last_incoming_message

    def put_outgoing_message(self, message: Message)->None:
        """
        Put a message in the outgoing messages queue.

        Args:
            message (Message): The message to put in the queue.
        """
        # Check the type of the message
        if not isinstance(message, Message):
            raise ValueError("message must be an instance of Message")

        with self.__lock:
            if not self.__is_open():
                return

            # Put the message in the queue
            self.__outgoing_messages_queue.put(message)

            # Set the pending outgoing message event
            self.__pending_outgoing_message_event.set()

    def __get_outgoing_message(self) -> str|None:
        """
        Get a message from the outgoing messages queue.

        Returns:
            str|None: The message from the outgoing messages queue or None if no message is available.
        """
        if self.__is_open():
            # Check if there is a pending outgoing message
            if not self.__pending_outgoing_message_event.is_set():
                return None

            # Get the message from the queue
            message = self.__outgoing_messages_queue.get()

            # Clear the pending outgoing message event
            if self.__outgoing_messages_queue.empty():
                self.__pending_outgoing_message_event.clear()

        # Log
        self.__logger.log(f"Sending message: {message}")

        # If the server is set, send the message to the server
        if self.__server is not None:
            self.__server.send_serial_outgoing_message(message)

        return message

    def send_message(self)->None:
        """
        Send a message to the serial port.
        """
        with self.__lock:
            if not self.__is_open():
                return

            # Check if there is a message to send
            if not self.__pending_outgoing_message_event.is_set():
                return

            # Get the message from the queue
            message = self.__get_outgoing_message()

            # Send the message to the serial port
            self.__serial.write(str(message).encode(ENCODE))

            # Wait for the message to be sent
            time.sleep(MESSAGE_DELAY)

    def receive_message(self)->None:
        """
        Receive a message from the serial port.
        """
        with self.__lock:
            if not self.__is_open():
                return

            # Check if there is a message to read
            if not self.__serial.in_waiting > 0:
                return None

            # Read the message from the serial port
            message_str = self.__serial.readline().decode(ENCODE).strip()

            # Split the message into type and content
            message_separator_idx = message_str.find(MESSAGE_HEADER_SEPARATOR)

            # Create the message object
            message = Message(
                message_str[:message_separator_idx],
                message_str[message_separator_idx + 1:],
            )

            # Put the message in the incoming messages queue
            self.__put_incoming_message(message)

    def get_stop_event(self)->Event:
        """
        Get the stop event status.

        Returns:
            Event: The event that indicates when to stop the communication.
        """
        return self.__stop_event

    def get_pending_incoming_message_event(self)->Event:
        """
        Get the pending incoming message event status.

        Returns:
            Event: The event that indicates when there is a pending incoming message.
        """
        return self.__pending_incoming_message_event

    def get_pending_outgoing_message_event(self)->Event:
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
        # Close the communication
        self.close()

def receiving_thread(stop_event: Event, serial_communication: SerialCommunication) -> None:
    """
    Thread to handle receiving messages from the serial port.
    """
    # Check the stop event
    if isinstance(stop_event, Event):
        raise ValueError("stop_event must be an instance of Event")

    while not stop_event.is_set():
        # Receive a message from the serial port
        serial_communication.receive_message()

        # Sleep for a short time to avoid busy waiting
        time.sleep(MESSAGE_DELAY)

def sending_thread(stop_event: Event, serial_communication: SerialCommunication) -> None:
    """
    Thread to handle sending messages to the serial port.
    """
    # Check the stop event
    if isinstance(stop_event, Event):
        raise ValueError("stop_event must be an instance of Event")

    while not stop_event.is_set():
        # Send a message to the serial port
        serial_communication.send_message()

        # Sleep for a short time to avoid busy waiting
        time.sleep(MESSAGE_DELAY)

def main(serial_communication: SerialCommunication) -> None:
    """
    Main function to run the script.
    """
    # Check the type of the serial communication
    if isinstance(serial_communication, SerialCommunication):
        raise ValueError("serial_communication must be an instance of SerialCommunication")

    # Get the stop event
    stop_event = serial_communication.get_stop_event()

    # Thread to handle receiving messages
    thread_1 = Thread(target=serial_communication.receive_message, args=(stop_event,serial_communication))
    thread_1.start()
    thread_1.join()

    # Thread to handle sending messages
    thread_2 = Thread(target=serial_communication.send_message, args=(stop_event,serial_communication))
    thread_2.start()
    thread_2.join()