from threading import Thread
from multiprocessing import Event, RLock, Queue
from io import TextIOWrapper
from datetime import datetime

from log.message import Message
from utils import check_type
from files import Files


class Logger:
    """
    Class to handle logging functionality.
    """
    # Get message from queue timeout
    GET_MESSAGE_FROM_QUEUE_TIMEOUT = 0.1

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
        self.__messages_queue = None

        # Initialize the write log event
        self.__write_log_event = Event()

        # Initialize the thread
        self.__thread = None

    def log(self, message: Message) -> None:
        """
        Put a log message in the queue.

        Args:
            message (Message): Message to put in the queue.
        """
        with self.__rlock:
            # Check if the stop event is set
            if self.__stop_event.is_set():
                # Write the message to the latest log file
                if not self.__file_path:
                    print("Logger is closed. Cannot log messages.")
                    return
                
                with open(self.__file_path, 'a') as file:
                    self.__write(file, str(message))
                return

            # If the opened event is not set, wait for it to be set
            if not self.__opened_event.is_set():
                self.__opened_event.wait()

            # Check the type of message
            check_type(message, Message)

            # Put the message in the queue
            self.__messages_queue.put(str(message))

            # Set the write log event
            self.__write_log_event.set()

    def __get_message(self) -> str|None:
        """
        Get a message from the queue.

        Returns:
            str|None: Message from the queue.
        """
        # Get the message from the queue
        with self.__rlock:
            if self.__messages_queue.empty():
                return None
            
            # Return the message from the queue
            return self.__messages_queue.get(timeout=self.GET_MESSAGE_FROM_QUEUE_TIMEOUT)

    @staticmethod
    def __write(file: TextIOWrapper, message: str) -> None:
        """
        Write a message to the log file.

        Args:
            file (TextIOWrapper): The file to write the message to.
            message (str): Message to log.
        """
        # Get the formatted time
        formatted_time = datetime.now().strftime('%H:%M:%S')

        # Check if the file is open
        if not file:
            print(f"Log file is not open. Must open it first.")
            return

        if not message:
            return

        # Write the message to the log file
        file.write(f"{formatted_time}: {message}\n")

        # Ensure immediate write
        file.flush()

    def __write_last_message(self, file: TextIOWrapper) -> None:
        """
        Write the last message to the log file.

        Args:
            file (TextIOWrapper): The file to write the message to.
        """
        # Get the last message from the queue
        message = self.__get_message()

        # Log the message
        self.__write(file, message)

    def __open(self) -> None:
        """
        Set the stop event to allow logging to start.
        """
        with self.__rlock:
            if self.__is_open():
                return

            # Clear the stop event
            self.__stop_event.clear()

            # Clear the write log event
            self.__write_log_event.clear()

    def __is_open(self) -> bool:
        """
        Check if the stop even is not set, indicating that's allowed to log messages.
        
        Returns:
            bool: True if the stop event is not set, False otherwise.
        """
        with self.__rlock:
            return not self.__stop_event.is_set()          

    def __close(self) -> None:
        """
        Set the stop event to stop logging messages.
        """
        with self.__rlock:
            # Check if the logger is already closed
            if self.__is_closed():
                return
            
            # Log the closing message
            self.log(Message("Logger is closing."))

            # Set the stop event
            self.__stop_event.set()

            # Clear the opened event
            self.__opened_event.clear()

            # Set the write log event
            self.__write_log_event.set()

    def __is_closed(self) -> bool:
        """
        Check if the logger is closed by checking if the stop event is set.

        Returns:
            bool: True if the stop event is set (indicating the logger is closed), False otherwise.
        """
        return not self.__is_open()

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
            self.log(Message(f"Logger opened at {self.__file_path}."))

            while self.__is_open():
                # Wait for the write log event to be set
                self.__write_log_event.wait()

                # Check if the stop event is set
                if self.__stop_event.is_set():
                    # Process any remaining messages in the queue
                    while not self.__messages_queue.empty():
                        # Write the last message to the log file
                        self.__write_last_message(file)
                    break

                # Write the last message to the log file
                self.__write_last_message(file)

                if self.__messages_queue.empty():
                    # If the queue is empty, clear the write log event
                    with self.__rlock:
                        if self.__stop_event.is_set():
                            break

                        self.__write_log_event.clear()

        # Close queue
        self.__messages_queue.close()

    def create_thread(self) -> None:
        """
        Create thread for the logger.
        """
        with self.__rlock:
            if self.__is_open():
                self.log(Message("Logger thread is already running."))
                return

            # Open the logger
            self.__open()

            # Create a thread for the logger
            self.__thread = Thread(target=self.__loop)
            self.__thread.start()

    def stop_thread(self) -> None:
        """
        Stop the logger thread.
        """
        with self.__rlock:
            # Close the logger
            self.__close()

    def __del__(self):
        """
        Destructor to close the thread if it's started.
        """
        self.stop_thread()