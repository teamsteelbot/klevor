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
            serial = SerialCommunication(logger=logger, server=server)

            # Start the serial communication
            serial.create_threads()
        else:
            serial = None

        # Create an instance of RPLIDAR
        rplidar = RPLIDAR(logger, server, serial)

        # Start the RPLIDAR
        rplidar.create_thread()

        # Wait indefinitely to keep the RPLIDAR running
        while True:
            sleep(1)

    except KeyboardInterrupt:
        # Handle keyboard interrupt to stop the server gracefully
        logger.log(Message("KeyboardInterrupt received, stopping the server..."))

    except Exception as e:
        # Log any exceptions that occur
        logger.log(f"An error occurred: {e}")

    finally:
        # Stop the RPLIDAR thread
        rplidar.stop_thread()

        # Stop the server thread
        if arg_server:
            server.stop_thread()

        # Stop the serial communication thread
        if arg_serial:
            serial.stop_threads()

        # Stop the logger thread
        logger.stop_thread()