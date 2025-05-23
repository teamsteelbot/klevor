import argparse
from multiprocessing import Process, Manager
from threading import Thread

from args import parse_args_as_dict
from yolo import ARGS_YOLO_INPUT_MODEL, ARGS_YOLO_VERSION
from yolo.args import add_yolo_input_model_argument, add_yolo_version_argument
from yolo.files import get_log_file_path
from yolo.hailo.object_detection import main as object_detection_main
from camera.images_queue import main as images_queue_main
from raspberry_pi_pico2.serial_communication import main as serial_communication_main
from log import main as log_main

def process_1_fn(serial_communication, logger):
    """
    Process 1: Serial communication with Raspberry Pi Pico and logging.
    """
    # Creating threads
    thread1 = Thread(target=serial_communication_main, args=(serial_communication,))
    thread2 = Thread(target=log_main, args=(logger,))

    # Starting threads
    thread1.start()
    thread2.start()

    # Waiting for threads to finish
    thread1.join()
    thread2.join()

def process_2_fn(images_queue):
    """
    Process 2: Images queue for camera.
    """
    images_queue_main(images_queue)

def process_3_fn(hailo):
    """
    Process 3: Object detection using YOLO.
    """
    hailo_main(hailo)

def main():
    """
    Main function to run the script.
    """
    parser = argparse.ArgumentParser(
        description="Klevor - WRO 2025 - Future Engineers Car")
    add_yolo_input_model_argument(parser)
    add_yolo_version_argument(parser)
    args = parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = args.get(ARGS_YOLO_INPUT_MODEL)

    # Get the YOLO version
    arg_yolo_version = args.get(ARGS_YOLO_VERSION)

    # Create a manager for shared objects
    with Manager() as manager:
        # Create the camera object with multiprocessing safety
        camera = manager.Camera()

        # Create the images queue with multiprocessing safety
        images_queue = manager.ImagesQueue(camera)

        # Raspberry Pi Pico serial communication wrapper with multiprocessing safety
        serial_communication = manager.SerialCommunication(images_queue)

        # Get the log file path
        log_file_path = get_log_file_path()

        # Get the stop event signal
        stop_event = serial_communication.get_stop_event()

        # Create the logger object with multiprocessing safety
        logger = manager.Logger(log_file_path, stop_event)

        # Create the Hailo object detection wrapper with multiprocessing safety
        #object_detection = manager.ObjectDetection(arg_yolo_input_model, arg_yolo_version, images_queue, stop_event)

        # Start the first process
        process_1 = Process(target=process_1_fn, args=(serial_communication, logger))
        process_1.start()
        process_1.join()

        # Start the second process
        process_2 = Process(target=process_2_fn, args=(images_queue,))
        process_2.start()
        process_2.join()

        # Start the third process
        process_3 = Process(target=process_3_fn, args=(hailo,))
        process_3.start()
        process_3.join()

        # Await for the stop event signal
        stop_event.wait()

if __name__ == "__main__":
    main()