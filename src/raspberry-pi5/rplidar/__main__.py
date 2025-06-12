from argparse import ArgumentParser

from args import Args
from rplidar import RPLIDAR
from server import RealtimeTrackerServer
from log import Logger
from log.message import Message
from time import sleep
from serial_communication import SerialCommunication

if __name__ == "__main__":
    parser = ArgumentParser(
        description="Script to test the RPLIDAR functionality and start it.")
    Args.add_server_argument(parser)
    Args.add_serial_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the server argument
    arg_server = Args.get_attribute_from_args(args, Args.SERVER)

    # Get the serial argument
    arg_serial = Args.get_attribute_from_args(args, Args.SERIAL)

    # Initialize variables for logger, server, serial communication, and RPLIDAR
    logger = None
    server = None
    serial = None
    rplidar = None

    try:
        # Create an instance of Logger
        logger = Logger()

        # Create a thread for the logger
        logger.create_thread()

        # Create an instance of the server
        if not arg_server:
            server = None
        else:
            server = RealtimeTrackerServer()

            # Start the server
            server.create_thread()

        # Create an instance of SerialCommunication if serial argument is provided
        if arg_serial:
            serial = SerialCommunication(logger=logger, server=server, port='/dev/ttyACM0')

            # Start the serial communication
            serial.create_threads()
        else:
            serial = None

        # Create an instance of RPLIDAR
        rplidar = RPLIDAR(logger, server, serial)

        # Start the RPLIDAR
        rplidar.create_thread()

        if not serial:
            while True:
                sleep(1)  # Sleep to prevent busy-waiting

        # Wait for the start message from SerialCommunication
        logger.log(Message("Waiting for start message from SerialCommunication..."))
        serial.wait_for_start_message()

        # Start the RPLIDAR thread
        rplidar.start_thread()
        logger.log(Message("RPLIDAR started successfully."))

        # Wait for the stop message from SerialCommunication
        serial.wait_for_stop_message()
        logger.log(Message("Received stop message from SerialCommunication, stopping RPLIDAR..."))

    except KeyboardInterrupt:
        # Handle keyboard interrupt to stop the server gracefully
        logger.log(Message("KeyboardInterrupt received. Stopping the server..."))

    except Exception as e:
        # Log any exceptions that occur
        logger.log(Message(f"An error occurred: {e}"))

    finally:
        # Stop the RPLIDAR thread
        if rplidar:
            rplidar.stop_thread()

        # Stop the server thread
        if arg_server and server:
            server.stop_thread()

        # Stop the serial communication thread
        if arg_serial and serial:
            serial.stop_threads()

        # Stop the logger thread
        if logger:
            logger.stop_thread()