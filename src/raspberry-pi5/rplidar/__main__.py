from argparse import ArgumentParser

from args import Args
from rplidar import RPLIDAR
from utils import check_type
from server import RealtimeTrackerServer
from log import Logger
from threading import Event

def main():
    """
    Main function to run the script.
    """
    parser = ArgumentParser(
        description="Script to test the RPLIDAR functionality and start it.")
    Args.add_server_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the server argument
    arg_server = Args.get_attribute_from_args(args, Args.SERVER)

    # Create a stop event
    stop_event = Event()

    # Create an instance of Logger
    logger = Logger(stop_event)

    # Create an instance of the server
    if arg_server:
        server = RealtimeTrackerServer()
        # Start the server
        server.start()
        print("Server started successfully.")

    # Create an instance of RPLIDAR
    rplidar = RPLIDAR()

    try:
        # Start the RPLIDAR
        rplidar.start()
        print("RPLIDAR started successfully.")
    except Exception as e:
        print(f"Error starting RPLIDAR: {e}")
        return

if __name__ == "__main__":
    main()