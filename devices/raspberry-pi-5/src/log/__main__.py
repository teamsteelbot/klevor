from multiprocessing import Event, Queue, Process
from time import sleep

from . import Logger
from .multiprocessing import writer_target

if __name__ == "__main__":
    # Create the required queues and events
    writer_messages_queue = Queue()
    writer_opened_event = Event()
    stop_event = Event()

    # Create a process for the writer
    writer_process = Process(target=writer_target, args=(writer_messages_queue, writer_opened_event, stop_event))
    writer_process.start()

    # Create an instance of Logger
    logger = Logger(writer_messages_queue)

    try:
        # Log a message using the logger
        logger.info("This is a test log message.")

        # Wait for a while to ensure the log messages are processed
        print("Writer is running. Press Ctrl+C to stop.")
        while True:
            # Keep the main thread alive to allow the writer to process messages
            logger.info("Writer is still running...")
            sleep(1)

    except KeyboardInterrupt:
        # Handle keyboard interrupt to stop the writer process gracefully
        print("KeyboardInterrupt received. Stopping writer process...")
        logger.warning("KeyboardInterrupt received. Stopping writer process.")

    except Exception as e:
        # Log any exceptions that occur
        logger.error(f"An error occurred: {e}")

    finally:
        # Stop the writer process and clean up
        stop_event.set()
        writer_process.join()
