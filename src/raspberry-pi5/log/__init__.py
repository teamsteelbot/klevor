from time import time
from multiprocessing import Lock, Event, Queue


class Logger:
    """
    Class to handle logging functionality.
    """
    __lock = None
    __file_path = None
    __messages_queue = None
    __file = None
    __stop_event = None
    __write_log_event = None

    def __init__(self, file_path: str, stop_event:Event):
        """
        Initialize the Logger class.

        Args:
            file_path (str): Path to the log file.
        """
        # Set the file path
        self.__file_path = file_path

        # Initialize the lock
        self.__lock = Lock()

        # Initialize the messages queue
        self.__messages_queue = Queue()

        # Check if the stop event is None
        if not isinstance(stop_event, Event):
            raise ValueError("stop_event must be an instance of Event")
        self.__stop_event = stop_event

        # Initialize the write log event
        self.__write_log_event = Event()

    def put_message(self, message: str):
        """
        Put a message in the queue.

        Args:
            message (str): Message to log.
        """
        with self.__lock:
            # Put the message in the queue
            self.__messages_queue.put(message)

            # Set the write log event
            self.__write_log_event.set()

    def __get_message(self):
        """
        Get a message from the queue.

        Returns:
            str: Message from the queue.
        """
        # Get the message from the queue
        return self.__messages_queue.get()

    def __log(self, message: str):
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

    def log(self):
        """
        Log the last message to the log file.
        """
        # Get the last message from the queue
        message = self.__get_message()

        # Log the message
        self.__log(message)

    def open(self):
        """
        Open the log file.
        """
        with self.__lock:
            if self.__file is None:
                self.__file = open(self.__file_path, 'a')
                print(f"Log file {self.__file_path} opened.")
            else:
                print(f"Log file {self.__file_path} is already open.")

    def close(self):
        """
        Close the log file.
        """
        with self.__lock:
            if self.__file:
                self.__file.close()
                self.__file = None

    def get_stop_event(self):
        """
        Get the stop event status.
        """
        return self.__stop_event

    def get_write_log_event(self):
        """
        Get the write log event status.
        """
        return self.__write_log_event

    def __del__(self):
        """
        Destructor to close the log file if it is open.
        """
        self.close()

def main(logger:Logger) -> None:
    """
    Main function to run the script.
    """
    # Check if the logger is None
    if not isinstance(logger, Logger):
        raise ValueError("logger must be an instance of Logger")

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
        logger.log()

        # Clear the write log event
        write_log_event.clear()

    # Close the log file
    logger.close()