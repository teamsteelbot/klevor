from argparse import ArgumentParser
from multiprocessing import Event, Process, Queue
from time import sleep

from .args import Args
from .multiprocessing import websocket_server_target
from ..log import Logger
from ..log.multiprocessing import writer_target

if __name__ == "__main__":
    parser = ArgumentParser(
        description="Script to test the WebSocketServer."
    )
    args = Args(parser)
    args.add_debug_argument()

    # Get the debug mode
    arg_debug = args.get_debug()

    # Create the required queues and events
    writer_messages_queue = Queue()
    writer_stop_event = Event()
    server_messages_queue = Queue()
    parking_event = Event()
    stop_event = Event()

    # Create a process for the writer
    writer_process = Process(
        target=writer_target, args=(
            arg_debug, writer_messages_queue, writer_stop_event)
    )
    writer_process.start()

    # Create an instance of Logger
    logger = Logger(writer_messages_queue, debug=arg_debug)

    # Create a process for the WebSocket server
    server_process = Process(
        target=websocket_server_target, args=(
            arg_debug, server_messages_queue, parking_event, stop_event,
            writer_messages_queue)
    )
    server_process.start()

    try:
        # Wait indefinitely to keep the server running
        print("WebSocketServer is running. Press Ctrl+C to stop.")
        while True:
            sleep(1)  # Sleep to prevent busy-waiting


    except KeyboardInterrupt:
        # Handle keyboard interrupt to stop the processes gracefully
        print(
            "KeyboardInterrupt received. Stopping websocket server and writer process..."
        )
        logger.warning(
            "KeyboardInterrupt received. Stopping websocket server and writer process."
        )


    except Exception as e:
        # Log any exceptions that occur
        logger.error(f"An error occurred: {e}")

    finally:
        # Stop the websocket server and writer process and clean up
        stop_event.set()
        server_process.join()
        writer_stop_event.set()
        writer_process.join()
