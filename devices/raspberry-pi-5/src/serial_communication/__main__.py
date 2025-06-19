from time import sleep

from ..log import Logger
from . import SerialCommunication

if __name__ == "__main__":
    # Create an instance of Logger
    logger = Logger()

    # Create an instance of SerialCommunication
    serial = SerialCommunication(logger=logger)

    try:
        # Start the logger thread
        logger.create_thread()

        # Create threads to handle receiving and sending messages
        serial.create_threads()

        # Start the serial communication
        serial.start()

        # Wait for the start message from SerialCommunication
        logger.log("Waiting for start message from SerialCommunication...")
        serial.wait_start_event()

        # Wait for the stop message from SerialCommunication
        serial.wait_stop_event()
        logger.log("Received stop message from SerialCommunication, stopping RPLIDAR...")

        # Wait indefinitely to keep the serial communication running
        print("Serial communication is running. Press Ctrl+C to stop.")
        while True:
            sleep(1)

    except KeyboardInterrupt as e:
        # Handle keyboard interrupt to stop the serial communication gracefully
        logger.warning(f"KeyboardInterrupt received. Stopping serial and logger threads.")

    finally:
        # Stop the serial communication threads gracefully
        if serial:
            serial.stop_threads()

        # Stop the logger thread gracefully
        if logger:
            logger.stop_thread()