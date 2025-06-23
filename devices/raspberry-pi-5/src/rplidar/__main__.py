from argparse import ArgumentParser

from ..args import Args, Flag
from . import RPLIDAR
from ..server import WebsocketsServer
from ..log import Logger
from time import sleep
from ..serial_communication import SerialCommunication

if __name__ == "__main__":
    parser = ArgumentParser(
        description="Script to test the RPLIDAR functionality and start it.")
    Args.add_server_argument(parser)
    Args.add_serial_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the server argument
    arg_server = Args.get_attribute_from_args_dict(args, Flag.SERVER)

    # Get the serial argument
    arg_serial = Args.get_attribute_from_args_dict(args, Flag.SERIAL)

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

        if not arg_server:
            server = None
        else:
            # Create an instance of the server
            server = WebsocketsServer(logger=logger)

            # Start the server
            server.create_thread()

        if not arg_serial:
            serial = None
        else:
            # Create an instance of SerialCommunication if serial argument is provided
            serial = SerialCommunication(logger=logger, server=server)

            # Start the serial communication
            serial.create_threads()

        # Create an instance of RPLIDAR
        rplidar = RPLIDAR(logger, server, serial)

        # Create the RPLIDAR thread
        rplidar.create_thread()

        if not serial:
            # Start the RPLIDAR
            rplidar.start()

            while True:
                sleep(1)  # Sleep to prevent busy-waiting
        else:
            # Wait for the start event
            serial.wait_start_event()

            # Start the RPLIDAR
            rplidar.start()

            # Wait for the stop event
            serial.wait_stop_event()

    except KeyboardInterrupt:
        # Handle keyboard interrupt to stop the server gracefully
        logger.warning("KeyboardInterrupt received. Stopping the server...")

    except Exception as e:
        # Log any exceptions that occur
        logger.error(f"An error occurred: {e}")

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