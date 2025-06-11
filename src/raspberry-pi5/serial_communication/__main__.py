from time import sleep

from log import Logger
from serial_communication import SerialCommunication

if __name__ == "__main__":
    # Create an instance of Logger
    logger = Logger()

    # Create an instance of SerialCommunication
    serial = SerialCommunication(logger=logger)

    try:
        # Create thread to handle receiving messages
        serial.create_receiving_thread()

        # Create thread to handle sending messages
        serial.create_sending_thread()

        # Wait indefinitely to keep the serial communication running
        while True:
            sleep(1)

    except KeyboardInterrupt as e:
        # Handle keyboard interrupt to stop the serial communication gracefully
        logger.log(f"KeyboardInterrupt received: {e}")

