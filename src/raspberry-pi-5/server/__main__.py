from multiprocessing import Event
from time import sleep

from server import RealtimeTrackerServer
from log import Logger
from log.message import Message

if __name__ == "__main__":
    # Create an instance of Logger
    logger = Logger()

    # Create an instance of RealtimeTrackerServer
    realtime_tracker_server = RealtimeTrackerServer(logger=logger)

    try:
        # Create a thread for the logger
        logger.create_thread()

        # Create a thread for the server
        realtime_tracker_server.create_thread()

        # Wait indefinitely to keep the server running
        print("Realtime Tracker Server is running. Press Ctrl+C to stop.")
        while True:
            sleep(1) # Sleep to prevent busy-waiting

    except KeyboardInterrupt:
        # Handle keyboard interrupt to stop the server gracefully
        logger.log(Message("KeyboardInterrupt received. Stopping the server..."))

    except Exception as e:
        # Log any exceptions that occur
        logger.log(Message(f"An error occurred: {e}"))

    finally:
        # Stop the server thread
        realtime_tracker_server.stop_thread()

        # Stop the logger thread
        logger.stop_thread()