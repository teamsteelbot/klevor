from time import time
from multiprocessing import Lock, Event, Queue

from raspberry_pi_pico2 import Message
from utils import check_type


class Logger:
    """
    Class to handle logging functionality.
    """

    def __init__(self, file_path: str, stop_event:Event):
        """
        Initialize the Logger class.

        Args:
            file_path (str): Path to the log file.
            stop_event (Event): Event to signal when to stop logging.
        """
        # Check the type of file_path
        check_type(file_path, str)
        self.__file_path = file_path

        # Check the type of stop_event
        check_type(stop_event, Event)
        self.__stop_event = stop_event

        # Initialize the lock
        self.__lock = Lock()

        # Initialize the messages queue
        self.__messages_queue = Queue()

        # Initialize the write log event
        self.__write_log_event = Event()

    def put_message(self, message: Message)->None:
        """
        Put a message in the queue.

        Args:
            message (Message): Message to put in the queue.
        """
        with self.__lock:
            # Check the type of message
            check_type(message, Message)

            # Put the message in the queue
            self.__messages_queue.put(str(message))

            # Set the write log event
            self.__write_log_event.set()

    def __get_message(self) -> str:
        """
        Get a message from the queue.

        Returns:
            str: Message from the queue.
        """
        # Get the message from the queue
        return self.__messages_queue.get()

    def __log(self, message: str)->None:
        """
        Log a message to the log file.

        Args:
            message (str): Message to log.
        """
        # Get the current UNIX time
        unix_time = int(time())

        # Check if the file is open
        if self.__file is None:
            print(f"Log file {self.__file_path} is not open. Must open it first.")
            return

        # Write the message to the log file
        self.__file.write(f"{unix_time}: {message}\n")

    def log_last_message(self)->None:
        """
        Log the last message to the log file.
        """
        # Get the last message from the queue
        message = self.__get_message()

        # Log the message
        self.__log(message)

    def open(self)->None:
        """
        Open the log file.
        """
        with self.__lock:
            if self.__file is None:
                self.__file = open(self.__file_path, 'a')
                print(f"Log file {self.__file_path} opened.")
            else:
                print(f"Log file {self.__file_path} is already open.")

    def close(self)->None:
        """
        Close the log file.
        """
        with self.__lock:
            if self.__file:
                self.__file.close()
                self.__file = None

    def get_stop_event(self)->Event:
        """
        Get the stop event status.

        Returns:
            Event: The stop event.
        """
        return self.__stop_event

    def get_write_log_event(self)->Event:
        """
        Get the write log event status.

        Returns:
            Event: The write log event.
        """
        return self.__write_log_event

    def get_sub_logger(self, tag: str) -> 'SubLogger':
        """
        Get a sub_logger with a specific tag.

        Args:
            tag (str): Tag for the log messages.

        Returns:
            SubLogger: An instance of SubLogger with the specified tag.
        """
        # Check the type of tag
        check_type(tag, str)

        return SubLogger(self, tag)

    def __del__(self):
        """
        Destructor to close the log file if it is open.
        """
        self.close()

def main(logger: Logger) -> None:
    """
    Main function to run the script.
    """
    # Check the type of logger
    check_type(logger, Logger)

    # Get the stop event
    stop_event = logger.get_stop_event()

    # Get the write log event
    write_log_event = logger.get_write_log_event()

    # Open the log file
    logger.open()

    while not stop_event.is_set():
        # Wait for the write log event to be set
        write_log_event.wait()

        # Log the last message
        logger.log_last_message()

        # Clear the write log event
        write_log_event.clear()

    # Close the log file
    logger.close()