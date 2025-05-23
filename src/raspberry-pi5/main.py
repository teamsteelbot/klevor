import argparse
from multiprocessing import Process, Manager, Event
from threading import Thread

from args import parse_args_as_dict, get_attribute_from_args
from raspberry_pi_pico2 import SerialCommunication, main as serial_communication_main
from yolo import ARGS_YOLO_VERSION, ARGS_DEBUG
from yolo.args import add_yolo_version_argument, add_debug_argument
from yolo.files import get_log_file_path
from yolo.hailo.object_detection import main as object_detection_main
from camera.images_queue import main as images_queue_main, ImagesQueue
from log import main as log_main, Logger

def process_1_fn(serial_communication: SerialCommunication):
    """
    Process 1: Serial communication with Raspberry Pi Pico.
    """
    # Check the type of serial communication
    if not isinstance(serial_communication, SerialCommunication):
        raise TypeError("serial_communication must be an instance of SerialCommunication")

    serial_communication_main(serial_communication)

def process_2_fn(images_queue: ImagesQueue, logger: Logger):
    """
    Process 2: Images queue for camera and logging.
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

def process_3_fn(debug: bool, yolo_version: str, images_queue: ImagesQueue, stop_event: Event):
    """
    Process 3: Hailo object detection.
    """
    # Check the debug mode
    if not isinstance(debug, bool):
        raise TypeError("debug must be a boolean")

    # Check the type of yolo version
    if not isinstance(yolo_version, str):
        raise TypeError("yolo_version must be a string")

    # Check the type of images queue
    if not isinstance(images_queue, ImagesQueue):
        raise TypeError("images_queue must be an instance of ImageQueue")

    # Check the type of stop event
    if not isinstance(stop_event, Event):
        raise TypeError("stop_event must be an instance of Event")

    object_detection_main(debug, yolo_version, images_queue, stop_event)


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

    # Create a manager for shared objects
    with Manager() as manager:
        # Create the stop event signal
        stop_event = manager.Event()

        # Get the log file path
        log_file_path = get_log_file_path()

        # Create the logger object with multiprocessing safety
        logger = manager.Logger(log_file_path, stop_event)

        # Create the camera object with multiprocessing safety
        camera = manager.Camera()

        # Create the images queue with multiprocessing safety
        images_queue = manager.ImagesQueue(stop_event, logger, camera)

        # Raspberry Pi Pico serial communication wrapper with multiprocessing safety
        serial_communication = manager.SerialCommunication(stop_event, logger, images_queue)

        # Start the first process
        process_1 = Process(target=process_1_fn, args=(serial_communication,))
        process_1.start()
        process_1.join()

        # Start the second process
        process_2 = Process(target=process_2_fn, args=(images_queue, logger))
        process_2.start()
        process_2.join()

        # Start the third process
        process_3 = Process(target=process_3_fn, args=(arg_debug, arg_yolo_version, images_queue, stop_event))
        process_3.start()
        process_3.join()

        # Await for the stop event signal
        stop_event.wait()

if __name__ == "__main__":
    main()