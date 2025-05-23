import argparse
from multiprocessing import Process, Queue, Manager

from camera import Camera
from raspberry_pi_pico2.serial_communication import SerialCommunication
from args import parse_args_as_dict
from yolo import ARGS_YOLO_INPUT_MODEL, ARGS_YOLO_VERSION
from yolo.args import add_yolo_input_model_argument, add_yolo_version_argument
from camera.images_queue import ImagesQueue
from yolo.hailo.object_detection import main as object_detection_main
from raspberry_pi_pico2.serial_communication import main as serial_communication_main

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
        # Create the camera instance
        camera = manager.Camera()

        # Images queue wrapper with multiprocessing safety
        images_queue = ImagesQueue(camera=camera)

        # Get the event signal to capture the image
        capture_image_event = images_queue.get_capture_image_event()

        # Raspberry Pi Pico serial communication wrapper with multiprocessing safety
        serial_communication = SerialCommunication(capture_image_event=capture_image_event)

        # Get the stop event signal
        stop_event = serial_communication.get_stop_event()

        # Start the object detection main process
        object_detection_process = Process(target=object_detection_main, args=(arg_yolo_input_model, arg_yolo_version, images_queue, stop_event))
        object_detection_process.start()
        object_detection_process.join()

        # Start the serial communication main process
        serial_process = Process(target=serial_communication_main, args=(serial_communication,))
        serial_process.start()
        serial_process.join()

        # Await for the stop event signal
        stop_event.wait()

if __name__ == "__main__":
    main()