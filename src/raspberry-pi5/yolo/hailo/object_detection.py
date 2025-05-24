from typing import Optional, Tuple, Dict
from functools import partial
from hailo_platform import (HEF, VDevice,
                            FormatType, HailoSchedulingAlgorithm)

import os
from multiprocessing import Event, Value
from pathlib import Path
import numpy as np
from PIL.Image import Image
from loguru import logger
from queue import Queue
import threading
import cv2
from typing import List

from camera.images_queue import ImagesQueue
from object_detection_utils import ObjectDetectionUtils
from yolo import YOLO_MODEL_G, YOLO_MODEL_M, YOLO_MODEL_R
from yolo.files import (get_model_hailo_suite_compiled_hef_file_path, get_hailo_labels_file_path)

# Currently models file paths
MODELS_NAME = [YOLO_MODEL_G, YOLO_MODEL_M, YOLO_MODEL_R]

import cv2
import numpy as np


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

    def preprocess(self, image: np.ndarray, model_w: int, model_h: int) -> np.ndarray:
        """
        Resize image with unchanged aspect ratio using padding.

        Args:
            image (np.ndarray): Input image.
            model_w (int): Model input width.
            model_h (int): Model input height.

        Returns:
            np.ndarray: Preprocessed and padded image.
        """
        img_h, img_w, _ = image.shape[:3]
        scale = min(model_w / img_w, model_h / img_h)
        new_img_w, new_img_h = int(img_w * scale), int(img_h * scale)
        image = cv2.resize(image, (new_img_w, new_img_h), interpolation=cv2.INTER_CUBIC)

        padded_image = np.full((model_h, model_w, 3), self.padding_color, dtype=np.uint8)
        x_offset = (model_w - new_img_w) // 2
        y_offset = (model_h - new_img_h) // 2
        padded_image[y_offset:y_offset + new_img_h, x_offset:x_offset + new_img_w] = image
        return padded_image

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
    __labels_path = None
    __images_queue = None

    def __init__(self, debug: bool, hef_file_path:str, labels_path: str, images_queue:ImagesQueue=None):
        """
        Initialize the Hailo handler class.
        """
        # Check the debug mode
        if not isinstance(debug, bool):
            raise TypeError("debug must be a boolean")

        # Check the HEF file path
        if not isinstance(hef_file_path, str):
            raise TypeError("hef_file_path must be a string")

        # Check the labels path
        if not isinstance(labels_path, str):
            raise TypeError("labels_path must be a string")

        # Check the images queue
        if not isinstance(images_queue, ImagesQueue):
            raise TypeError("images_queue must be an instance of ImagesQueue")

def preprocess(
    images: List[np.ndarray],
    cap: cv2.VideoCapture,
    batch_size: int,
    input_queue: queue.Queue,
    width: int,
    height: int,
    utils: ObjectDetectionUtils
) -> None:
    """
    Preprocess and enqueue images or camera frames into the input queue as they are ready.

    Args:
        images (List[np.ndarray], optional): List of images as NumPy arrays.
        camera (bool, optional): Boolean indicating whether to use the camera stream.
        batch_size (int): Number of images per batch.
        input_queue (queue.Queue): Queue for input images.
        width (int): Model input width.
        height (int): Model input height.
        utils (ObjectDetectionUtils): Utility class for object detection preprocessing.
    """
    if cap is None:
        preprocess_images(images, batch_size, input_queue, width, height, utils)
    else:
        preprocess_from_cap(cap, batch_size, input_queue, width, height, utils)

    input_queue.put(None)  # Add sentinel value to signal end of input

def preprocess_from_cap(cap: cv2.VideoCapture, batch_size: int, input_queue: queue.Queue, width: int, height: int, utils: ObjectDetectionUtils) -> None:
    """
    Process frames from the camera stream and enqueue them.

    Args:
        batch_size (int): Number of images per batch.
        input_queue (queue.Queue): Queue for input images.
        width (int): Model input width.
        height (int): Model input height.
        utils (ObjectDetectionUtils): Utility class for object detection preprocessing.
    """
    frames = []
    processed_frames = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frames.append(frame)
        processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        processed_frame = utils.preprocess(processed_frame, width, height)
        processed_frames.append(processed_frame)

        if len(frames) == batch_size:
            input_queue.put((frames, processed_frames))
            processed_frames, frames = [], []


def preprocess_images(images: List[np.ndarray], batch_size: int, input_queue: queue.Queue, width: int, height: int, utils: ObjectDetectionUtils) -> None:
    """
    Process a list of images and enqueue them.

    Args:
        images (List[np.ndarray]): List of images as NumPy arrays.
        batch_size (int): Number of images per batch.
        input_queue (queue.Queue): Queue for input images.
        width (int): Model input width.
        height (int): Model input height.
        utils (ObjectDetectionUtils): Utility class for object detection preprocessing.
    """
    for batch in divide_list_to_batches(images, batch_size):
        input_tuple = ([image for image in batch], [utils.preprocess(image, width, height) for image in batch])
        input_queue.put(input_tuple)

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
    if cap is not None:
        # Create a named window
        cv2.namedWindow("Output", cv2.WND_PROP_FULLSCREEN)

        # Set the window to fullscreen
        cv2.setWindowProperty("Output", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        if save_stream_output:
            output_path.mkdir(exist_ok=True)
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
             # Define the codec and create VideoWriter object
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            # Save the output video in the output path
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps == 0:  # If FPS is not available, set a default value
                print(f"fps: {fps}")
                fps = 20.0
            out = cv2.VideoWriter(str(output_path / 'output_video.avi'), fourcc, fps, (frame_width, frame_height))

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
        
        if cap is not None:
            # Display output
            cv2.imshow("Output", frame_with_detections)
            if save_stream_output:
                out.write(frame_with_detections)
        else:
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

    if cap is not None and save_stream_output:
            out.release()  # Release the VideoWriter object
    output_queue.task_done()  # Indicate that processing is complete
\__image_stream_queue = None
    __hef = None
    __target = None
    __infer_model = None
    __output_type = None
    __send_original_frame = None

    def __init__(
        self, hef_path: str, image_stream_queue: ImageStreamQueue, batch_size: int = 1,
        input_type: Optional[str] = None, output_type: Optional[Dict[str, str]] = None,
        send_original_frame: bool = False) -> None:
        """
        Initialize the HailoAsyncInference class with the provided HEF model
        file path and input/output queues.

        Args:
            hef_path (str): Path to the HEF model file.
            image_stream_queue (ImageStreamQueue): Queue for input images.
            batch_size (int): Batch size for inference. Defaults to 1.
            input_type (Optional[str]): Format type of the input stream.
                                        Possible values: 'UINT8', 'UINT16'.
            output_type Optional[dict[str, str]] : Format type of the output stream.
                                         Possible values: 'UINT8', 'UINT16', 'FLOAT32'.
        """
        # Set the image stream queue
        self.__image_stream_queue = image_stream_queue

        # Create the VDevice parameters
        params = VDevice.create_params()

        # Set the scheduling algorithm to round-robin to activate the scheduler
        params.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN

        # Enable multi-processing service
        params.group_id = "SHARED"
        params.multi_process_service = True

        # Set the VDevice parameters
        self.__target = VDevice(params)

        # Set the HEF model
        self.__hef = HEF(hef_path)
        self.__infer_model = self.__target.create_infer_model(hef_path)
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

    def get_vstream_info(self) -> Tuple[list, list]:

        """
        Get information about input and output stream layers.

        Returns:
            Tuple[list, list]: List of input stream layer information, List of
                               output stream layer information.
        """
        return (
            self.__hef.get_input_vstream_infos(),
            self.__hef.get_output_vstream_infos()
        )

    def get_hef(self) -> HEF:
        """
        Get the object's HEF file

        Returns:
            HEF: A HEF (Hailo Executable File) containing the model.
        """
        return self.__hef

    def get_input_shape(self) -> Tuple[int, ...]:
        """
        Get the shape of the model's input layer.

        Returns:
            Tuple[int, ...]: Shape of the model's input layer.
        """
        return self.__hef.get_input_vstream_infos()[0].shape  # Assumes one input

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

    def _get_output_type_str(self, output_info) -> str:
        if self.output_type is None:
            return str(output_info.format.type).split(".")[1].lower()
        else:
            self.output_type[output_info.name].lower()

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



def infer(
    input,
    save_stream_output: bool,
    net_path: str,
    labels_path: str,
    batch_size: int,
) -> None:
    """
    Initialize queues, HailoAsyncInference instance, and run the inference.

    Args:
        images (List[Image.Image]): List of images to process.
        net_path (str): Path to the HEF model file.
        labels_path (str): Path to a text file containing labels.
        batch_size (int): Number of images per batch.
        output_path (Path): Path to save the output images.
    """
    det_utils = ObjectDetectionUtils(labels_path)

    input_queue = queue.Queue()
    output_queue = queue.Queue()

    hailo_inference = HailoAsyncInference(
        net_path, input_queue, output_queue, batch_size, send_original_frame=True
    )
    height, width, _ = hailo_inference.get_input_shape()

    preprocess_thread = threading.Thread(
        target=preprocess,
        args=(images, cap, batch_size, input_queue, width, height, det_utils)
    )
    postprocess_thread = threading.Thread(
        target=postprocess,
        args=(output_queue, cap, save_stream_output, det_utils)
    )

    preprocess_thread.start()
    postprocess_thread.start()

    hailo_inference.run()
    
    preprocess_thread.join()
    output_queue.put(None)  # Signal process thread to exit
    postprocess_thread.join()

    logger.info('Inference was successful!')

def infer(image: Image, infer_queue: Queue, hailo_handler: HailoHandler) -> None:
    return

def main(debug: bool, yolo_version: str, images_queue: ImagesQueue, stop_event: Event) -> None:
    """
    Main function to run the script.
    """
    # Check the debug mode
    if not isinstance(debug, bool):
        raise TypeError("debug must be a boolean")

    # Check the type of yolo version
    if not isinstance(yolo_version, str):
        raise TypeError("yolo_version must be a string")

    # Check the type of images queue
    if not isinstance(images_queue, ImagesQueue):
        raise ValueError("images_queue must be an instance of ImagesQueue")

    # Check the type of stop event
    if not isinstance(stop_event, Event):
        raise TypeError("stop_event must be an instance of Event")

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
    for model_name in MODELS_NAME:
        # Get the HEF file path
        hef_file_path = hef_file_paths.get(model_name)

        # Get the labels file path
        labels_file_path = labels_file_paths.get(model_name)

        # Check if the HEF file path exists
        if not os.path.exists(hef_file_path):
            raise ValueError(f"HEF file {hef_file_path} does not exist.")

        # Check if the labels file path exists
        if not os.path.exists(labels_file_path):
            raise ValueError(f"Labels file {labels_file_path} does not exist.")

        # Create the Hailo handler
        hailo_handlers[model_name] = HailoHandler(debug, hef_file_path, labels_file_path, images_queue)

    # Get the pending image event from the images queue
    pending_image_event = images_queue.get_pending_image_event()

    # Create the infer queues dictionary
    infer_queues = dict()
    for model_name in MODELS_NAME:
        # Create the infer queue for the model
        infer_queues[model_name] = Queue()

    # Wait for the stop event
    while not stop_event.is_set():
        # Wait for the pending image event
        pending_image_event.wait()

        # Get the image from the images queue
        image = images_queue.get_input_image()

        # Iterate over the models
        pool=[]
        for model_name in MODELS_NAME:
            # Get the infer queue for the model
            infer_queue = infer_queues.get(model_name)

            # Get the Hailo handler for the model
            hailo_handler = hailo_handlers.get(model_name)

            # Thread to handle the inference
            thread=threading.Thread(target=infer, args=(image, infer_queue, hailo_handler))

            # Append the thread to the pool
            pool.append(thread)

            # Start the thread
            thread.start()

        # Wait for all threads to finish
        for thread in pool:
            thread.join()

        # Check which inference were successful
        for model_name in MODELS_NAME:
            # Get the infer queue for the model
            infer_queue = infer_queues.get(model_name)

            # Iterate over the inference results
            while not infer_queue.empty():
                result = infer_queue.get()
                if result is None:
                    continue

                # Add the result to the images queue
                images_queue.put_output_inference(result)