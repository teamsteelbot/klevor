from multiprocessing import Event
from time import sleep

from log import Logger
from log.sub_logger import SubLogger
from log.message import Message
    
if __name__ == "__main__":
    # Create an instance of Logger
    logger = Logger()

    # Create a sub-logger for this module
    sub_logger = SubLogger(logger, "Test")

    try:
        # Create a thread for the logger
        logger.create_thread()

        # Log a message using the sub-logger
        sub_logger.log("This is a test log message.")

        # Log a message using the main logger
        logger.log(Message("This is a test log message from the main logger."))

        # Wait for a while to ensure the log messages are processed
        print("Logger is running. Press Ctrl+C to stop.")
        while True:
            sleep(1)

    except KeyboardInterrupt:
        # Handle keyboard interrupt to stop the logger thread gracefully
        logger.log(Message("KeyboardInterrupt received. Stopping logger thread."))

    except Exception as e:
        # Log any exceptions that occur
        logger.log(Message(f"An error occurred: {e}"))

    finally:
        # Stop the logger thread gracefully
        if logger:
            logger.stop_thread()