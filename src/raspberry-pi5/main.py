import argparse
import os
from multiprocessing import Process, Manager, Event
from threading import Thread

from args import parse_args_as_dict, get_attribute_from_args
from raspberry_pi_pico2 import SerialCommunication, main as serial_communication_main
from server import RealtimeTrackerServer
from yolo import ARGS_YOLO_VERSION, ARGS_DEBUG
from env import ENV_YOLO_VERSION, ENV_DEBUG
from yolo.args import add_yolo_version_argument, add_debug_argument
from yolo.files import get_log_file_path
from yolo.hailo.object_detection import main as object_detection_main
from camera.images_queue import main as images_queue_main, ImagesQueue
from log import main as log_main, Logger
from server import main as server_main

def process_1_fn(serial_communication: SerialCommunication, server: RealtimeTrackerServer|None):
    """
    Process 1: Serial communication with Raspberry Pi Pico.

    Args:
        serial_communication (SerialCommunication): The serial communication object.
        server (RealtimeTrackerServer|None): The WebSocket server for real-time tracking updates.
    """
    # Check the type of serial communication
    if not isinstance(serial_communication, SerialCommunication):
        raise TypeError("serial_communication must be an instance of SerialCommunication")

    # Check the type of server
    if server is not None and not isinstance(server, RealtimeTrackerServer):
        raise TypeError("server must be an instance of RealtimeTrackerServer or None")

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
    if not isinstance(images_queue, ImagesQueue):
        raise TypeError("images_queue must be an instance of ImageQueue")

    # Check the type of logger
    if not isinstance(logger, Logger):
        raise TypeError("logger must be an instance of Logger")

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

def process_3_fn(images_queue: ImagesQueue, parking_event: Event, stop_event: Event):
    """
    Process 3: Hailo object detection.

    Args:
        images_queue (ImagesQueue): The images queue object.
        parking_event (Event): The event signal for parking detection.
        stop_event (Event): The event signal to stop processing.
    """
    # Check the type of images queue
    if not isinstance(images_queue, ImagesQueue):
        raise TypeError("images_queue must be an instance of ImageQueue")

    # Check the type of parking event
    if not isinstance(parking_event, Event):
        raise TypeError("parking_event must be an instance of Event")

    # Check the type of stop event
    if not isinstance(stop_event, Event):
        raise TypeError("stop_event must be an instance of Event")

    object_detection_main(images_queue, parking_event, stop_event)


def main():
    """
    Main function to run the script.
    """
    parser = argparse.ArgumentParser(
        description="Klevor - WRO 2025 - Future Engineers Car")
    add_yolo_version_argument(parser)
    add_debug_argument(parser)
    args = parse_args_as_dict(parser)

    # Get the YOLO version
    arg_yolo_version = get_attribute_from_args(args, ARGS_YOLO_VERSION)

    # Get the debug mode
    arg_debug = get_attribute_from_args(args, ARGS_DEBUG)

    # Set the debug mode and YOLO version as environment variables
    os.environ[ENV_DEBUG] = str(arg_debug).lower()
    os.environ[ENV_YOLO_VERSION] = arg_yolo_version

    # Create a manager for shared objects
    with Manager() as manager:
        # Create the parking event signal
        parking_event = manager.Event()

        # Create the stop event signal
        stop_event = manager.Event()

        # Get the log file path
        log_file_path = get_log_file_path()

        # Create the logger object with multiprocessing safety
        logger = manager.Logger(log_file_path, stop_event)

        # Create the websocket server
        if not arg_debug:
            server = None
        else:
            server = manager.WebsocketServer(stop_event, logger)

        # Create the camera object with multiprocessing safety
        camera = manager.Camera(logger)

        # Create the images queue with multiprocessing safety
        images_queue = manager.ImagesQueue(stop_event, logger, camera, server=server)

        # Raspberry Pi Pico serial communication wrapper with multiprocessing safety
        serial_communication = manager.SerialCommunication(parking_event, stop_event, logger, images_queue, server=server)

        # Start the first process
        process_1 = Process(target=process_1_fn, args=(serial_communication, server))
        process_1.start()
        process_1.join()

        # Start the second process
        process_2 = Process(target=process_2_fn, args=(images_queue, logger))
        process_2.start()
        process_2.join()

        # Start the third process
        process_3 = Process(target=process_3_fn, args=(images_queue, parking_event, stop_event))
        process_3.start()
        process_3.join()

        # Await for the stop event signal
        stop_event.wait()

if __name__ == "__main__":
    main()