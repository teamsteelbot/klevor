from threading import Thread
from multiprocessing import Event, RLock, Queue
from typing import Optional, TextIO

from log.message import Message, Category
from utils import check_type
from files import Files


class Logger:
    """
    Class to handle logging functionality.
    """
    # Get message from queue timeout
    GET_MESSAGE_FROM_QUEUE_TIMEOUT = 0.01

    def __init__(self):
        """
        Initialize the Logger class.
        """
        # Create the reentrant lock
        self.__rlock = RLock()

        # Create the opened event
        self.__opened_event = Event()

        # Create the stop event
        self.__stop_event = Event()
        self.__stop_event.set()

        # Initialize the messages queue
        self.__messages_queue: Queue[Message]|None = None

        # Initialize the write log event
        self.__write_log_event = Event()

        # Initialize the thread
        self.__thread = None

    def log(self, content: str, category: Category = Category.INFO, tag: Optional[str] = None) -> None:
        """
        Put a log message in the queue.

        Args:
            content (str): Content of the log message.
            category (Category): Category of the log message.
            tag (Optional[str]): Optional tag for the log message.
        """
        with self.__rlock:
            # Check the type of content
            check_type(content, str)

            # Check the type of category
            check_type(category, Category)

            # Check the type of tag
            check_type(tag, str) if tag else None

            # Create a message object
            message = Message(content, category, tag)

            # Check if the logger has stopped
            if self.is_stopped():
                # Write the message to the latest log file
                if not self.__file_path:
                    print("Log file path is not set. Must create thread first.")
                    return
                
                with open(self.__file_path, 'a') as file:
                    self.__write(file, str(message))
                return

            # If the opened event is not set, wait for it to be set
            if not self.__opened_event.is_set():
                self.__opened_event.wait()

            # Put the message in the queue
            self.__messages_queue.put(message)

            # Set the write log event
            self.__write_log_event.set()

    def info(self, content: str, tag: Optional[str] = None) -> None:
        """
        Log an informational message.

        Args:
            content (str): Content of the log message.
            tag (Optional[str]): Optional tag for the log message.
        """
        self.log(content, Category.INFO, tag)

    def error(self, content: str, tag: Optional[str] = None) -> None:
        """
        Log an error message.

        Args:
            content (str): Content of the log message.
            tag (Optional[str]): Optional tag for the log message.
        """
        self.log(content, Category.ERROR, tag)

    def warning(self, content: str, tag: Optional[str] = None) -> None:
        """
        Log a warning message.

        Args:
            content (str): Content of the log message.
            tag (Optional[str]): Optional tag for the log message.
        """
        self.log(content, Category.WARNING, tag)

    def debug(self, content: str, tag: Optional[str] = None) -> None:
        """
        Log a debug message.

        Args:
            content (str): Content of the log message.
            tag (Optional[str]): Optional tag for the log message.
        """
        self.log(content, Category.DEBUG, tag)

    def __get_message(self) -> Message|None:
        """
        Get a message from the queue.

        Returns:
            Message|None: Message from the queue.
        """
        # Get the message from the queue
        with self.__rlock:
            if self.__messages_queue.empty():
                return None
            
            # Return the message from the queue
            return self.__messages_queue.get(timeout=self.GET_MESSAGE_FROM_QUEUE_TIMEOUT)

    @staticmethod
    def __write(file: TextIO, message: Message) -> None:
        """
        Write a message to the log file.

        Args:
            file (TextIO): The file to write the message to.
            message (Message): Message to log.
        """
        # Check if the file is open
        if not file:
            print(f"Log file is not open. Must open it first.")
            return

        if not message:
            print("No message to log.")
            return

        # Write the message to the log file
        file.write(message + "\n")

        # Ensure immediate write
        file.flush()

    def __write_last_message(self, file: TextIO) -> None:
        """
        Write the last message to the log file.

        Args:
            file (TextIO): The file to write the message to.
        """
        # Get the last message from the queue
        message = self.__get_message()

        # Log the message
        self.__write(file, message)

    def __loop(self, file_path: str = Files.get_log_file_path()) -> None:
        """
        Main loop for the logger to write messages to the log file.

        Args:
            file_path (str): Path to the log file.
        """
        # Initialize the messages queue
        self.__messages_queue = Queue()

        # Check the type of file_path
        check_type(file_path, str)
        self.__file_path = file_path

        # Ensure the file exists
        Files.ensure_file_exists(self.__file_path)

        # Open the log file in append mode
        with open(self.__file_path, 'a') as file:
            # Set the opened event
            self.__opened_event.set()
            self.debug(f"Logger opened at {self.__file_path}.")

            while self.is_running():
                # Wait for the write log event to be set
                self.__write_log_event.wait()

                # Check if the stop event is set
                if self.is_stopped():
                    # Process any remaining messages in the queue
                    while not self.__messages_queue.empty():
                        # Write the last message to the log file
                        self.__write_last_message(file)
                    break

                # Write the last message to the log file
                self.__write_last_message(file)

                # If the queue is empty, clear the write log event
                if self.__messages_queue.empty():
                    self.__write_log_event.clear()

        # Close queue
        self.__messages_queue.close()

    def __start(self) -> None:
        """
        Set the stop event to allow logging to start.
        """
        with self.__rlock:
            if self.is_running():
                return

            # Clear the stop event
            self.__stop_event.clear()

            # Clear the write log event
            self.__write_log_event.clear()

    def is_running(self) -> bool:
        """
        Check if the stop event is not set, indicating that's allowed to log messages.

        Returns:
            bool: True if the stop event is not set, False otherwise.
        """
        with self.__rlock:
            return not self.__stop_event.is_set()

    def __stop(self) -> None:
        """
        Set the stop event to stop logging messages.
        """
        with self.__rlock:
            # Check if the logger has already stopped
            if self.is_stopped():
                return

            # Log the closing message
            self.debug("Logger is closing.")

            # Set the stop event
            self.__stop_event.set()

            # Clear the opened event
            self.__opened_event.clear()

            # Set the write log event
            self.__write_log_event.set()

    def is_stopped(self) -> bool:
        """
        Check if the logger is stopped by checking if the stop event is set.

        Returns:
            bool: True if the stop event is set (indicating the logger is stopped), False otherwise.
        """
        return not self.is_running()

    def create_thread(self) -> None:
        """
        Create thread for the logger.
        """
        with self.__rlock:
            # Start the logger
            self.__start()

            # Create a thread for the logger
            self.__thread = Thread(target=self.__loop)
            self.__thread.start()

    def stop_thread(self) -> None:
        """
        Stop the logger thread.
        """
        with self.__rlock:
            # Stop the logger
            self.__stop()

            # Set thread to None if it exists
            if self.__thread:
                self.__thread.join()
                self.__thread = None

    def __del__(self):
        """
        Destructor to stop the thread if it's started.
        """
        self.stop_thread() if self.__thread else None