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

    # Start the WebSocket server
    realtime_tracker_server.create_thread()

    try:
        # Create a thread for the logger
        logger.create_thread()

        # Create a thread for the server
        realtime_tracker_server.create_thread()

        # Wait indefinitely to keep the server running
        while True:
            sleep(1)  # Sleep to prevent busy-waiting

    except KeyboardInterrupt:
        # Handle keyboard interrupt to stop the server gracefully
        logger.log(Message("KeyboardInterrupt received, stopping the server..."))

    except Exception as e:
        # Log any exceptions that occur
        logger.log(f"An error occurred: {e}")

    finally:
        # Stop the logger thread
        logger.stop_thread()

        # Stop the server thread
        realtime_tracker_server.stop_thread()