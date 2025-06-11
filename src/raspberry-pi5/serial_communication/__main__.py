from time import sleep

from log import Logger
from serial_communication import SerialCommunication

if __name__ == "__main__":
    # Create an instance of Logger
    logger = Logger()

    # Create an instance of SerialCommunication
    serial = SerialCommunication(logger=logger)

    try:
        # Create threads to handle receiving and sending messages
        serial.create_threads()

        # Wait indefinitely to keep the serial communication running
        while True:
            sleep(1)

    except KeyboardInterrupt as e:
        # Handle keyboard interrupt to stop the serial communication gracefully
        logger.log(f"KeyboardInterrupt received: {e}")

    finally:
        # Stop the serial communication threads gracefully
        if serial:
            serial.stop_threads()

        # Stop the logger thread gracefully
        if logger:
            logger.stop_thread()