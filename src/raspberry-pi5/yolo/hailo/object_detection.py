from typing import Optional, Tuple, Dict
from functools import partial
from hailo_platform import (HEF, VDevice,
                            FormatType, HailoSchedulingAlgorithm)

import os
from multiprocessing import Event
from pathlib import Path
from PIL.Image import Image
from loguru import logger
from queue import Queue
import threading
import cv2
import numpy as np


from camera import WIDTH, HEIGHT
from camera.images_queue import ImagesQueue
from env import get_debug_mode
from yolo import YOLO_MODEL_G, YOLO_MODEL_M, YOLO_MODEL_R, get_model_classes_color_palette
from yolo.files import (get_model_hailo_suite_compiled_hef_file_path, get_hailo_labels_file_path)
from yolo.hailo import IMAGE_PADDING_COLOR

# Currently models file paths
MODELS_NAME = [YOLO_MODEL_G, YOLO_MODEL_M, YOLO_MODEL_R]
NO_PARKING_MODELS_NAME = [YOLO_MODEL_G, YOLO_MODEL_R]
PARKING_MODELS_NAME = [YOLO_MODEL_M]

class ObjectDetectionUtils:
    def __init__(self, labels_path: str, padding_color: tuple = (114, 114, 114),
                 label_font: str = "LiberationSans-Regular.ttf"):
        """
        Initialize the ObjectDetectionUtils class.

        Args:
            labels_path (str): Path to the labels file.
            padding_color (tuple): RGB color for padding. Defaults to (114, 114, 114).
            label_font (str): Path to the font used for labeling. Defaults to "LiberationSans-Regular.ttf".
        """
        self.labels = self.get_labels(labels_path)
        self.padding_color = padding_color
        self.label_font = label_font

    def get_labels(self, labels_path: str) -> list:
        """
        Load labels from a file.

        Args:
            labels_path (str): Path to the labels file.

        Returns:
            list: List of class names.
        """
        with open(labels_path, 'r', encoding="utf-8") as f:
            class_names = f.read().splitlines()
        return class_names

    def draw_detection(self, image: np.ndarray, box: list, cls: int, score: float, color: tuple, scale_factor: float):
        """
        Draw box and label for one detection.

        Args:
            image (np.ndarray): Image to draw on.
            box (list): Bounding box coordinates.
            cls (int): Class index.
            score (float): Detection score.
            color (tuple): Color for the bounding box.
            scale_factor (float): Scale factor for coordinates.
        """
        label = f"{self.labels[cls]}: {score:.2f}%"
        ymin, xmin, ymax, xmax = box
        ymin, xmin, ymax, xmax = int(ymin * scale_factor), int(xmin * scale_factor), int(ymax * scale_factor), int(
            xmax * scale_factor)
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, 2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, label, (xmin + 4, ymin + 20), font, 0.5, color, 1, cv2.LINE_AA)

    def denormalize_and_rm_pad(self, box: list, size: int, padding_length: int, input_height: int,
                               input_width: int) -> list:
        """
        Denormalize bounding box coordinates and remove padding.

        Args:
            box (list): Normalized bounding box coordinates.
            size (int): Size to scale the coordinates.
            padding_length (int): Length of padding to remove.
            input_height (int): Height of the input image.
            input_width (int): Width of the input image.

        Returns:
            list: Denormalized bounding box coordinates with padding removed.
        """
        for i, x in enumerate(box):
            box[i] = int(x * size)
            if (input_width != size) and (i % 2 != 0):
                box[i] -= padding_length
            if (input_height != size) and (i % 2 == 0):
                box[i] -= padding_length

        return box

    def draw_detections(self, detections: dict, image: np.ndarray, min_score: float = 0.45, scale_factor: float = 1):
        """
        Draw detections on the image.

        Args:
            detections (dict): Detection results containing 'detection_boxes', 'detection_classes', 'detection_scores', and 'num_detections'.
            image (np.ndarray): Image to draw on.
            min_score (float): Minimum score threshold. Defaults to 0.45.
            scale_factor (float): Scale factor for coordinates. Defaults to 1.

        Returns:
            np.ndarray: Image with detections drawn.
        """
        boxes = detections['detection_boxes']
        classes = detections['detection_classes']
        scores = detections['detection_scores']

        # Values used for scaling coords and removing padding
        img_height, img_width = image.shape[:2]
        size = max(img_height, img_width)
        padding_length = int(abs(img_height - img_width) / 2)

        for idx in range(detections['num_detections']):
            if scores[idx] >= min_score:
                color = generate_color(classes[idx])
                scaled_box = self.denormalize_and_rm_pad(boxes[idx], size, padding_length, img_height, img_width)
                self.draw_detection(image, scaled_box, classes[idx], scores[idx] * 100.0, color, scale_factor)

        return image

class HailoHandler:
    """
    Class to handle Hailo inference.
    """
    __debug = None
    __hef_file_path = None
    __hef = None
    __labels_path = None
    __images_queue = None
    __class_colors = None
    __padding_color = None
    __target = None
    __infer_model = None
    __output_type = None
    __send_original_frame = None
    __batch_size = None

    def __init__(self, debug: bool, hef_file_path:str, labels_path: str, images_queue:ImagesQueue,
                 class_colors: dict[int, tuple[int,int,int]], padding_color:tuple = IMAGE_PADDING_COLOR,
                 multi_threading: bool = True, multi_processing: bool = False, batch_size: int = 1,
                 input_type: Optional[str] = None, output_type: Optional[Dict[str, str]] = None,
                 send_original_frame: bool = False
                 ):
        """
        Initialize the Hailo handler class.
        """
        # Check the debug mode
        if not isinstance(debug, bool):
            raise TypeError("debug must be a boolean")
        self.__debug = debug

        # Check the HEF file path
        if not isinstance(hef_file_path, str):
            raise TypeError("hef_file_path must be a string")
        if not os.path.exists(hef_file_path):
            raise ValueError(f"HEF file {hef_file_path} does not exist.")
        self.__hef_file_path = hef_file_path

        # Check the labels path
        if not isinstance(labels_path, str):
            raise TypeError("labels_path must be a string")
        if not os.path.exists(labels_path):
            raise ValueError(f"Labels file {labels_path} does not exist.")
        self.__labels_path = labels_path

        # Check the images queue
        if not isinstance(images_queue, ImagesQueue):
            raise TypeError("images_queue must be an instance of ImagesQueue")
        self.__images_queue = images_queue

        # Check the class colors
        if not isinstance(class_colors, dict):
            raise TypeError("class_colors must be a dictionary")
        self.__class_colors = class_colors

        # Check the padding color
        if not isinstance(padding_color, tuple):
            raise TypeError("padding_color must be a tuple")
        if len(padding_color) != 3:
            raise ValueError("padding_color must be a tuple of length 3")
        self.__padding_color = padding_color

        # Set the batch size
        if not isinstance(batch_size, int):
            raise TypeError("batch_size must be an integer")
        if batch_size < 1:
            raise ValueError("batch_size must be greater than 0")
        self.__batch_size = batch_size

        # Create the VDevice parameters
        params = VDevice.create_params()

        # Set the scheduling algorithm to round-robin to activate the scheduler
        params.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN

        # Set the group ID to SHARED
        if multi_threading or multi_processing:
            params.group_id = "SHARED"

        # Enable multi-processing service
        if multi_processing:
            params.multi_process_service = True

        # Set the VDevice parameters
        self.__target = VDevice(params)

        # Set the HEF model
        self.__hef = HEF(self.__hef_file_path)
        self.__infer_model = self.__target.create_infer_model(self.__hef_file_path)
        self.__infer_model.set_batch_size(batch_size)

        # Set the input and output types
        if input_type is not None:
            self._set_input_type(input_type)
        if output_type is not None:
            self._set_output_type(output_type)
        self.__output_type = output_type

        # Send the original frame
        self.__send_original_frame = send_original_frame

    def _set_input_type(self, input_type: Optional[str] = None) -> None:
        """
        Set the input type for the HEF model. If the model has multiple inputs,
        it will set the same type of all of them.

        Args:
            input_type (Optional[str]): Format type of the input stream.
        """
        self.__infer_model.input().set_format_type(getattr(FormatType, input_type))

    def _set_output_type(self, output_type_dict: Optional[Dict[str, str]] = None) -> None:
        """
        Set the output type for the HEF model. If the model has multiple outputs,
        it will set the same type for all of them.

        Args:
            output_type_dict (Optional[dict[str, str]]): Format type of the output stream.
        """
        for output_name, output_type in output_type_dict.items():
            self.__infer_model.output(output_name).set_format_type(
                getattr(FormatType, output_type)
            )

    def _get_output_type_str(self, output_info) -> str | None:
        """
        Get the output type string for the HEF model.
        """
        if self.__output_type is None:
            return str(output_info.format.type).split(".")[1].lower()
        else:
            self.__output_type[output_info.name].lower()

    def get_input_shape(self) -> Tuple[int, ...]:
        """
        Get the shape of the model's input layer.

        Returns:
            Tuple[int, ...]: Shape of the model's input layer.
        """
        return self.__hef.get_input_vstream_infos()[0].shape  # Assumes one input

    def preprocess(self, image: Image, width: int=WIDTH, height: int=HEIGHT) -> np.ndarray:
        """
        Resize image with unchanged aspect ratio using padding.

        Args:
            image (Image): Input image.
            width (int): Model input width.
            height (int): Model input height.

        Returns:
            np.ndarray: Preprocessed and padded image.
        """
        # Convert image to numpy array
        image = np.array(image)

        # Resize image with unchanged aspect ratio using padding
        img_height, img_width, _ = image.shape[:3]
        scale = min(width / img_width, height / img_height)
        new_img_width, new_img_height = int(img_width * scale), int(img_height * scale)
        image = cv2.resize(image, (new_img_width, new_img_height), interpolation=cv2.INTER_CUBIC)

        # Calculate padding and create padded image
        padded_image = np.full((height, width, 3), self.__padding_color, dtype=np.uint8)
        x_offset =(height - new_img_width) // 2
        y_offset = (height - new_img_height) // 2
        padded_image[y_offset:y_offset + new_img_height, x_offset:x_offset + new_img_width] = image
        return padded_image

    # TO CHECK

    def callback(
        self, completion_info, bindings_list: list, input_batch: list,
    ) -> None:
        """
        Callback function for handling inference results.

        Args:
            completion_info: Information about the completion of the
                             inference task.
            bindings_list (list): List of binding objects containing input
                                  and output buffers.
            input_batch (list): The processed batch of images.
        """
        if completion_info.exception:
            logger.error(f'Inference error: {completion_info.exception}')
        else:
            for i, bindings in enumerate(bindings_list):
                # If the model has a single output, return the output buffer.
                # Else, return a dictionary of output buffers, where the keys are the output names.
                if len(bindings._output_names) == 1:
                    result = bindings.output().get_buffer()
                else:
                    result = {
                        name: np.expand_dims(
                            bindings.output(name).get_buffer(), axis=0
                        )
                        for name in bindings._output_names
                    }
                self.__output_queue.put((input_batch[i], result))

    async def run(self) -> None:
        with self.__infer_model.configure() as configured_infer_model:
            while True:
                batch_data = self.__input_queue.get()
                if batch_data is None:
                    break  # Sentinel value to stop the inference loop

                if self.send_original_frame:
                    original_batch, preprocessed_batch = batch_data
                else:
                    preprocessed_batch = batch_data

                bindings_list = []
                for frame in preprocessed_batch:
                    bindings = self._create_bindings(configured_infer_model)
                    bindings.input().set_buffer(np.array(frame))
                    bindings_list.append(bindings)

                configured_infer_model.wait_for_async_ready(timeout_ms=10000)
                job = configured_infer_model.run_async(
                    bindings_list, partial(
                        self.callback,
                        input_batch=original_batch if self.send_original_frame else preprocessed_batch,
                        bindings_list=bindings_list
                    )
                )
            job.wait(10000)  # Wait for the last job

    def _create_bindings(self, configured_infer_model) -> object:
        """
        Create bindings for input and output buffers.

        Args:
            configured_infer_model: The configured inference model.

        Returns:
            object: Bindings object with input and output buffers.
        """
        if self.output_type is None:
            output_buffers = {
                output_info.name: np.empty(
                    self.infer_model.output(output_info.name).shape,
                    dtype=(getattr(np, self._get_output_type_str(output_info)))
                )
            for output_info in self.hef.get_output_vstream_infos()
            }
        else:
            output_buffers = {
                name: np.empty(
                    self.infer_model.output(name).shape,
                    dtype=(getattr(np, self.output_type[name].lower()))
                )
            for name in self.output_type
            }
        return configured_infer_model.create_bindings(
            output_buffers=output_buffers
        )

    def postprocess(
        output_queue: queue.Queue,
        cap: cv2.VideoCapture,
        save_stream_output: bool,
        utils: ObjectDetectionUtils
    ) -> None:
        """
        Process and visualize the output results.

        Args:
            output_queue (queue.Queue): Queue for output results.
            camera (bool): Flag indicating if the input is from a camera.
            save_stream_output (bool): Flag indicating if the camera output should be saved.
            utils (ObjectDetectionUtils): Utility class for object detection visualization.
        """
        image_id = 0
        out = None
        output_path = Path('output')

        if (cap is None):
            # Create output directory if it doesn't exist
            output_path.mkdir(exist_ok=True)

        while True:
            result = output_queue.get()
            if result is None:
                break  # Exit the loop if sentinel value is received

            original_frame, infer_results = result

            # Deals with the expanded results from hailort versions < 4.19.0
            if len(infer_results) == 1:
                infer_results = infer_results[0]

            detections = utils.extract_detections(infer_results)

            frame_with_detections = utils.draw_detections(
                detections, original_frame,
            )

            cv2.imwrite(str(output_path / f"output_{image_id}.png"), frame_with_detections)

            # Wait for key press "q"
            image_id += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                # Close the window and release the camera
                if save_stream_output:
                    out.release()  # Release the VideoWriter object
                cap.release()
                cv2.destroyAllWindows()
                break

        output_queue.task_done()  # Indicate that processing is complete

def infer(image: Image, infer_queue: Queue, hailo_handler: HailoHandler, height:int, width:int) -> None:
    """
    Run inference on the image using Hailo.
    """
    #det_utils = ObjectDetectionUtils(labels_path)

    # Preprocess image
    preprocessed_image = hailo_handler.preprocess(image, width, height)

    # Run inference
    hailo_inference.run


    postprocess_thread = threading.Thread(
        target=postprocess,
        args=(output_queue, cap, save_stream_output, det_utils)
    )


    hailo_inference.run()

    preprocess_thread.join()
    output_queue.put(None)  # Signal process thread to exit
    postprocess_thread.join()

def main(images_queue: ImagesQueue, parking_event: Event, stop_event: Event) -> None:
    """
    Main function to run the script.
    """
    # Check the type of images queue
    if not isinstance(images_queue, ImagesQueue):
        raise ValueError("images_queue must be an instance of ImagesQueue")

    # Check the type of stop event
    if not isinstance(stop_event, Event):
        raise TypeError("stop_event must be an instance of Event")

    # Get the debug mode from the environment variable
    debug = get_debug_mode()

    # Get the required file paths
    hef_file_paths = dict()
    labels_file_paths = dict()
    for model_name in MODELS_NAME:
        # Get the HEF file paths
        hef_file_paths[model_name] = get_model_hailo_suite_compiled_hef_file_path(model_name, yolo_version)

        # Get the labels file paths
        labels_file_paths[model_name] = get_hailo_labels_file_path(model_name)

    # Create the Hailo handlers
    hailo_handlers = dict()
    hailo_input_shapes = dict()
    infer_queues = dict()
    for model_name in MODELS_NAME:
        # Get the HEF file path
        hef_file_path = hef_file_paths.get(model_name)

        # Get the labels file path
        labels_file_path = labels_file_paths.get(model_name)

        # Create the infer queue for the model
        infer_queues[model_name] = Queue()

        # Get the model class colors
        model_class_colors = get_model_classes_color_palette(model_name)

        # Create the Hailo handler
        hailo_handler = HailoHandler(debug, hef_file_path, labels_file_path, images_queue, model_class_colors)
        hailo_handlers[model_name] = hailo_handler

        # Get the input shape of the model
        height, width, _ = hailo_handler.get_input_shape()
        hailo_input_shapes[model_name] = (height, width)

    # Get the pending image event from the images queue
    pending_image_event = images_queue.get_pending_image_event()

    # Wait for the stop event
    while not stop_event.is_set():
        # Wait for the pending image event
        pending_image_event.wait()

        # Check if the parking event is set
        if parking_event.is_set():
            models_name = PARKING_MODELS_NAME
        else:
            models_name = NO_PARKING_MODELS_NAME

        # Get the image from the images queue
        image = images_queue.get_input_image()

        # Iterate over the models
        pool=[]
        for model_name in models_name:
            # Get the infer queue for the model
            infer_queue = infer_queues.get(model_name)

            # Get the Hailo handler for the model
            hailo_handler = hailo_handlers.get(model_name)

            # Get the input shape of the model
            height, width = hailo_input_shapes.get(model_name)

            # Thread to handle the inference
            thread=threading.Thread(target=infer, args=(image, infer_queue, hailo_handler, height, width))

            # Append the thread to the pool
            pool.append(thread)

            # Start the thread
            thread.start()

        # Wait for all threads to finish
        for thread in pool:
            thread.join()

        # Check which inference were successful
        for model_name in models_name:
            # Get the infer queue for the model
            infer_queue = infer_queues.get(model_name)

            # Iterate over the inference results
            while not infer_queue.empty():
                result = infer_queue.get()
                if result is None:
                    continue

                # Add the result to the images queue
                images_queue.put_output_inference(result)