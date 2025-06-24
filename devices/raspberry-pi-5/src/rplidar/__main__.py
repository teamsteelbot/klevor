from argparse import ArgumentParser
from multiprocessing import Event, Process, Queue
from time import sleep

from .multiprocessing import rplidar_target
from ..args import Args, Flag
from ..log import Logger
from ..log.multiprocessing import writer_target
from ..server.multiprocessing import websocket_server_target

if __name__ == "__main__":
    parser = ArgumentParser(
        description="Script to test the RPLIDAR functionality and start it."
    )
    Args.add_server_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the server argument
    arg_server = Args.get_attribute_from_args_dict(args, Flag.SERVER)

    # Create the required queues and events
    writer_messages_queue = Queue()
    writer_stop_event = Event()
    rplidar_update_measures_event = Event()
    rplidar_measures_queue = Queue()
    server_messages_queue = Queue() if arg_server else None
    start_event = Event()
    parking_event = Event()
    stop_event = Event()

    # Create a process for the writer
    writer_process = Process(
        target=writer_target, args=(
            writer_messages_queue, writer_stop_event)
    )
    writer_process.start()

    # Create an instance of Logger
    logger = Logger(writer_messages_queue)

    # Create a process for the WebSocket server
    if not arg_server:
        server_process = None

    else:
        server_process = Process(
            target=websocket_server_target, args=(
                server_messages_queue, parking_event, stop_event,
                writer_messages_queue)
        )
        server_process.start()

    # Create a process for the RPLIDAR
    rplidar_process = Process(
        target=rplidar_target,
        args=(rplidar_update_measures_event, rplidar_measures_queue,
              start_event, stop_event, writer_messages_queue,
              server_messages_queue if arg_server else None,)
    )
    rplidar_process.start()

    try:
        # Wait indefinitely to keep the serial communication running
        print("RPLIDAR is running. Press Ctrl+C to stop.")
        while True:
            sleep(1)  # Sleep to prevent busy-waiting

    except KeyboardInterrupt:
        # Handle keyboard interrupt to stop the processes gracefully
        print(
            "KeyboardInterrupt received. Stopping RPLIDAR, server and writer process..."
        )
        logger.warning(
            "KeyboardInterrupt received. Stopping RPLIDAR, server and writer process..."
        )

    except Exception as e:
        # Log any exceptions that occur
        logger.error(f"An error occurred: {e}")

    finally:
        # Stop the RPLIDAR, server and writer process and clean up
        stop_event.set()
        rplidar_process.join()
        server_process.join() if arg_server else None
        writer_stop_event.set()
        writer_process.join()
