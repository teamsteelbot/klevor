import argparse
from multiprocessing import Process, Manager, Event
from threading import Thread

from camera.images_queue import main as images_queue_main, ImagesQueue
from env import Env
from log import main as log_main, Logger
from serial import SerialCommunication, main as serial_communication_main
from server import RealtimeTrackerServer
from server import main as server_main
from utils import check_type
from yolo.args import Args
from yolo.files import Files
from yolo.hailo.object_detection import main as object_detection_main


def process_1_fn(serial_communication: SerialCommunication, server: RealtimeTrackerServer | None):
    """
    Process 1: Serial communication with Raspberry Pi Pico.

    Args:
        serial_communication (SerialCommunication): The serial communication object.
        server (RealtimeTrackerServer|None): The WebSocket server for real-time tracking updates.
    """
    # Check the type of serial communication
    check_type(serial_communication, SerialCommunication)

    # Check the type of server
    if server:
        check_type(server, RealtimeTrackerServer)

    # Check if the server is None
    if server is None:
        serial_communication_main(serial_communication)
    else:
        # Creating threads
        pool = [
            Thread(target=serial_communication_main, args=(serial_communication,)),
            Thread(target=server_main, args=(server,))
        ]

        # Starting threads
        for thread in pool:
            thread.start()

        # Waiting for threads to finish
        for thread in pool:
            thread.join()


def process_2_fn(images_queue: ImagesQueue, logger: Logger):
    """
    Process 2: Images queue for camera and logging.

    Args:
        images_queue (ImagesQueue): The images queue object.
        logger (Logger): The logger object for logging messages.
    """
    # Check the type of images queue
    check_type(images_queue, ImagesQueue)

    # Check the type of logger
    check_type(logger, Logger)

    # Creating threads
    pool = [
        Thread(target=images_queue_main, args=(images_queue,)),
        Thread(target=log_main, args=(logger,))
    ]

    # Starting threads
    for thread in pool:
        thread.start()

    # Waiting for threads to finish
    for thread in pool:
        thread.join()


def process_3_fn(logger: Logger, images_queue: ImagesQueue, parking_event: Event, stop_event: Event):
    """
    Process 3: Hailo object detection.

    Args:
        logger (Logger): The logger object for logging messages.
        images_queue (ImagesQueue): The images queue object.
        parking_event (Event): The event signal for parking detection.
        stop_event (Event): The event signal to stop processing.
    """
    # Check the type of logger
    check_type(logger, Logger)

    # Check the type of images queue
    check_type(images_queue, ImagesQueue)

    # Check the type of parking event
    check_type(parking_event, Event)

    # Check the type of stop event
    check_type(stop_event, Event)

    object_detection_main(logger, images_queue, parking_event, stop_event)

def main():
    """
    Main function to run the script.
    """
    parser = argparse.ArgumentParser(
        description="Klevor - WRO 2025 - Future Engineers Car")
    Args.add_yolo_version_argument(parser)
    Args.add_debug_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the YOLO version
    arg_yolo_version = Args.get_attribute_from_args(args, Args.VERSION)

    # Get the debug mode
    arg_debug = Args.get_attribute_from_args(args, Args.DEBUG)

    # Set the debug mode and YOLO version as environment variables
    Env.set_yolo_version(arg_yolo_version)
    Env.set_debug_mode(arg_debug)

    # Create a manager for shared objects
    with Manager() as manager:
        try:
            # Create the parking event signal
            parking_event = manager.Event()

            # Create the stop event signal
            stop_event = manager.Event()

            # Get the log file path
            log_file_path = Files.get_log_file_path()

            # Create the logger object with multiprocessing safety
            logger = manager.Logger(log_file_path, stop_event)

            # Create the websocket server
            server = manager.WebsocketServer(stop_event, logger) if arg_debug else None

            # Create the camera object with multiprocessing safety
            camera = manager.Camera(logger)

            # Create the images queue with multiprocessing safety
            images_queue = manager.ImagesQueue(stop_event, logger, camera, server=server)

            # Raspberry Pi Pico serial communication wrapper with multiprocessing safety
            serial_communication = manager.SerialCommunication(parking_event, stop_event, logger, images_queue,
                                                            server=server)

            # First process
            process_1 = Process(target=process_1_fn, args=(serial_communication, server))

            # Second process
            process_2 = Process(target=process_2_fn, args=(images_queue, logger))

            # Third process
            process_3 = Process(target=process_3_fn, args=(logger, images_queue, parking_event, stop_event))

            # Start the processes
            processes = [process_1, process_2, process_3]
            for process in processes:
                process.start()

            # Wait for the processes to finish
            for process in processes:
                process.join()
        except KeyboardInterrupt:
            # Handle keyboard interrupt to stop all processes gracefully
            print("KeyboardInterrupt received. Stopping all processes...")
            stop_event.set()

        except Exception as e:
            print(f"An error occurred: {e}")
            logger.put_message(f"An error occurred: {e}")
            stop_event.set()
        finally:
            # Ensure all processes are terminated
            for process in processes:
                if process.is_alive():
                    process.terminate()
                    process.join()


if __name__ == "__main__":
    main()
