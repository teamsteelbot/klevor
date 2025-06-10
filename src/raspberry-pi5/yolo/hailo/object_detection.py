import threading
from multiprocessing import Queue, Event

from camera.images_queue import ImagesQueue
from env import Env
from log import Logger
from utils import check_type
from yolo import Yolo
from yolo.files import Files
from yolo.hailo import Hailo

def listen_images_queue(images_queue: ImagesQueue, stop_event: Event, parking_event: Event,
                        hailo_handlers: dict[str, Hailo],
                        )-> None:
    """
    Listen to the images queue and process the images based on the parking event.
    """
    # Check the type of images queue
    check_type(images_queue, ImagesQueue)

    # Check the type of stop event
    check_type(stop_event, Event)

    # Check the type of parking event
    check_type(parking_event, Event)

    # Get the pending image event from the images queue
    pending_image_event = images_queue.get_pending_image_event()

    # Wait for the stop event
    stopped_hailo_handlers = False
    while not stop_event.is_set():
        # Wait for the pending image event
        pending_image_event.wait()

        # Get the image from the images queue
        image = images_queue.get_input_image(Hailo.preprocess)

        # Check if the parking event is set
        if parking_event.is_set():
            # Put the model M image in the Hailo handler input queue
            hailo_handlers[Yolo.MODEL_M].put_image(image)

            if stopped_hailo_handlers:
                continue

            # Stop the Hailo handlers for G and R models
            hailo_handlers[Yolo.MODEL_G].stop()
            hailo_handlers[Yolo.MODEL_R].stop()
            stopped_hailo_handlers = True
        else:
            # Put the model G and R images in the Hailo handler input queues
            hailo_handlers[Yolo.MODEL_G].put_image(image)
            hailo_handlers[Yolo.MODEL_R].put_image(image)

def main(logger: Logger, images_queue: ImagesQueue, parking_event: Event, stop_event: Event) -> None:
    """
    Main function to run the script.
    """
    # Check the type of logger
    check_type(logger, Logger)

    # Check the type of images queue
    check_type(images_queue, ImagesQueue)

    # Check the type of stop event
    check_type(stop_event, Event)

    # Check the type of parking event
    check_type(parking_event, Event)

    # Get the YOLO version from the environment variables
    yolo_version = Env.get_yolo_version()

    # Get the required file paths
    hef_file_paths = dict()
    labels_file_paths = dict()
    for model_name in Yolo.MODELS_NAME:
        # Get the HEF file paths
        hef_file_paths[model_name] = Files.get_model_hailo_suite_compiled_hef_file_path(model_name, yolo_version)

        # Get the labels file paths
        labels_file_paths[model_name] = Files.get_hailo_labels_file_path(model_name)

    # Create the Hailo handlers
    hailo_handlers = dict()
    hailo_input_shapes = dict()
    input_queues = dict()
    hailo_stop_events = dict()
    for model_name in Yolo.MODELS_NAME:
        # Get the HEF file path
        hef_file_path = hef_file_paths.get(model_name)

        # Get the labels file path
        labels_file_path = labels_file_paths.get(model_name)

        # Create the queues for the model
        input_queue = Queue()
        input_queues[model_name] = input_queue

        # Get the model class colors
        model_class_colors = Yolo.get_model_classes_color_palette(model_name)

        # Create the Hailo handler
        hailo_handler = Hailo(model_name, hef_file_path, labels_file_path, model_class_colors,
                              images_queue=images_queue, logger=logger, input_queue=input_queue,
                              put_output_inference_fn=images_queue.put_output_inference)
        hailo_handlers[model_name] = hailo_handler

        # Get the input shape of the model
        height, width, _ = hailo_handler.get_input_shape()
        hailo_input_shapes[model_name] = (height, width)

        # Get the stop event for the model
        hailo_stop_events[model_name] = hailo_handler.get_stop_event()

    # Create the threads
    threads = []
    thread_1 = threading.Thread(target=listen_images_queue, args=(images_queue, stop_event, parking_event, hailo_handlers))
    threads.append(thread_1)

    for model_name in Yolo.MODELS_NAME:
        # Get the Hailo handler for the model
        hailo_handler = hailo_handlers.get(model_name)

        # Create a thread to handle the inference
        thread = threading.Thread(target=hailo_handler.run, args=())
        threads.append(thread)

    # Start the threads
    for thread in threads:
        thread.start()

    # Wait for the threads to finish
    for thread in threads:
        thread.join()