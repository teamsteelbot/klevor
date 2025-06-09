import queue
from multiprocessing import Event
from typing import Optional
from functools import partial
from hailo_platform import (HEF, VDevice,
                            FormatType, HailoSchedulingAlgorithm)

from PIL.Image import Image
import cv2
import numpy as np

from camera.images_queue import ImagesQueue
from log import Logger
from model.image_bounding_boxes import ImageBoundingBoxes
from opencv.preprocessing import Preprocessing
from utils import check_type
from yolo import Yolo
from yolo.files import Files

class Hailo:
    """
    Class to handle Hailo inference.
    """
    # Logger configuration
    LOG_TAG = "Hailo"

    # Image allowed extensions
    IMAGE_ALLOWED_EXTENSIONS: tuple = ('.jpg', '.png', '.bmp', '.jpeg')

    # Padding color
    IMAGE_PADDING_COLOR: tuple[int, int, int] = (0, 0, 0)

    # Currently models file paths
    MODELS_NAME = [Yolo.MODEL_G, Yolo.MODEL_M, Yolo.MODEL_R]
    NO_PARKING_MODELS_NAME = [Yolo.MODEL_G, Yolo.MODEL_R]
    PARKING_MODELS_NAME = [Yolo.MODEL_M]

    # Batch size
    BATCH_SIZE = 1

    # Job timeout
    TIMEOUT = 10000

    def __init__(self, model_name:str, hef_file_path:str, labels_path: str, class_colors: dict[int, tuple[int,int,int]],
                 multi_threading: bool = True, multi_processing: bool = False, images_queue: ImagesQueue = None,
                 logger: Logger = None, batch_size: int = BATCH_SIZE, input_type: Optional[str] = None,
                 output_type: Optional[dict[str, str]] = None, input_queue: queue.Queue = None,
                 put_output_inference_fn = None,
                 ):
        """
        Initialize the Hailo handler class.

        Args:
            model_name (str): Name of the YOLO model.
            hef_file_path (str): Path to the HEF file.
            labels_path (str): Path to the labels file.
            class_colors (dict[int, tuple[int, int, int]]): Dictionary mapping class IDs to RGB colors.
            multi_threading (bool): Whether to enable multi-threading. Defaults to True.
            multi_processing (bool): Whether to enable multi-processing. Defaults to False.
            images_queue (ImagesQueue): Queue for images. Defaults to None.
            logger (Logger): Logger instance for logging messages. Defaults to None.
            batch_size (int): Batch size for inference. Defaults to BATCH_SIZE.
            input_type (Optional[str]): Format type of the input stream. Defaults to None.
            output_type (Optional[dict[str, str]]): Format type of the output stream. Defaults to None.
            input_queue (queue.Queue): Input queue for preprocessed images. Defaults to None.
            put_output_inference_fn: Function to put output inference results into the queue. Defaults to None.
        """
        # Check the type of model name
        check_type(model_name, str)
        self.__model_name = model_name

        # Check the HEF file path
        check_type(hef_file_path, str)
        Files.ensure_path_exists(hef_file_path)
        self.__hef_file_path = hef_file_path

        # Check the labels path
        check_type(labels_path, str)
        Files.ensure_path_exists(labels_path)
        self.__labels_path = labels_path

        # Load the labels
        self.__labels = Yolo.get_labels_from_txt(self.__labels_path)

        # Check the type of images queue
        check_type(images_queue, ImagesQueue)
        self.__images_queue = images_queue

        # Check the type of logger
        check_type(logger, Logger)
        self.__logger = logger.get_sub_logger(self.LOG_TAG)

        # Check the type of class colors
        check_type(class_colors, dict)
        self.__class_colors = class_colors

        # Check the type of batch size
        check_type(batch_size, int)
        self.__batch_size = batch_size

        # Check the type of input queue
        check_type(input_queue, queue.Queue)
        self.__input_queue = input_queue

        # Create the stop event
        self.__stop_event = Event()

        # Set the put output inference function
        self.__put_output_inference_fn = put_output_inference_fn

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
        if not input_type:
            self._set_input_type(input_type)
        if not output_type:
            self._set_output_type(output_type)
        self.__output_type = output_type

    def get_stop_event(self) -> Event:
        """
        Get the stop event for the Hailo handler.

        Returns:
            Event: The stop event.
        """
        return self.__stop_event

    def _set_input_type(self, input_type: Optional[str] = None) -> None:
        """
        Set the input type for the HEF model. If the model has multiple inputs,
        it will set the same type of all of them.

        Args:
            input_type (Optional[str]): Format type of the input stream.
        """
        self.__infer_model.input().set_format_type(getattr(FormatType, input_type))

    def _set_output_type(self, output_type_dict: Optional[dict[str, str]] = None) -> None:
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

        Args:
            output_info: Information about the output stream.
        """
        if not self.__output_type:
            return str(output_info.format.type).split(".")[1].lower()
        else:
            self.__output_type[output_info.name].lower()

    def get_input_shape(self) -> tuple[int, ...]:
        """
        Get the shape of the model's input layer.

        Returns:
            tuple[int, ...]: Shape of the model's input layer.
        """
        return self.__hef.get_input_vstream_infos()[0].shape  # Assumes one input

    @classmethod
    def preprocess(cls, image: Image, width: int=Preprocessing.WIDTH, height: int=Preprocessing.HEIGHT) -> np.ndarray:
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
        padded_image = np.full((height, width, 3), cls.IMAGE_PADDING_COLOR, dtype=np.uint8)
        x_offset =(height - new_img_width) // 2
        y_offset = (height - new_img_height) // 2
        padded_image[y_offset:y_offset + new_img_height, x_offset:x_offset + new_img_width] = image
        return padded_image

    def put_image(self, preprocessed_image: np.ndarray) -> None:
        """
        Put a preprocessed image into the input queue.

        Args:
            preprocessed_image (np.ndarray): Preprocessed image to be put into the queue.
        """
        # Check the type of preprocessed image
        check_type(preprocessed_image, np.ndarray)

        self.__input_queue.put(preprocessed_image)

    def callback(
        self, completion_info, bindings, preprocessed_image: np.ndarray
    ) -> None:
        """
        Callback function for handling inference results.

        Args:
            completion_info: Information about the completion of the
                             inference task.
            bindings: Binding objects containing input
                                  and output buffers.
            preprocessed_image (np.ndarray): Preprocessed image used for inference.
        """
        if completion_info.exception:
            self.__logger.log(f'Inference error: {completion_info.exception}')
            return

        # If the model has a single output, return the output buffer.
        if len(bindings._output_names) == 1:
            result = bindings.output().get_buffer()

        # Else, return a dictionary of output buffers, where the keys are the output names.
        else:
            result = {
                name: np.expand_dims(
                    bindings.output(name).get_buffer(), axis=0
                )
                for name in bindings._output_names
            }
        self.__put_output_inference_fn(self.__model_name, ImageBoundingBoxes.from_hailo(result))

    def run(self) -> None:
        """
        Run the inference loop.

        This method continuously retrieves batches of images from the input queue,
        preprocesses them, and runs inference using the configured infer model.
        """
        with self.__infer_model.configure() as configured_infer_model:
            while not self.__stop_event.is_set():
                # Get a preprocessed image from the input queue
                preprocessed_image = self.__input_queue.get()

                # Create the bindings for the input and output buffers
                bindings = self._create_bindings(configured_infer_model)
                bindings.input().set_buffer(np.array(preprocessed_image))

                configured_infer_model.wait_for_async_ready(timeout_ms=self.TIMEOUT)
                job = configured_infer_model.run_async(
                    bindings, partial(
                        self.callback,
                        preprocessed_image=preprocessed_image,
                        bindings=bindings
                    )
                )
            job.wait(self.TIMEOUT)  # Wait for the last job


    def _create_bindings(self, configured_infer_model) -> object:
        """
        Create bindings for input and output buffers.

        Args:
            configured_infer_model: The configured inference model.

        Returns:
            object: Bindings object with input and output buffers.
        """
        if not self.__output_type:
            output_buffers = {
                output_info.name: np.empty(
                    self.__infer_model.output(output_info.name).shape,
                    dtype=(getattr(np, self._get_output_type_str(output_info)))
                )
            for output_info in self.__hef.get_output_vstream_infos()
            }
        else:
            output_buffers = {
                name: np.empty(
                    self.__infer_model.output(name).shape,
                    dtype=(getattr(np, self.__output_type[name].lower()))
                )
            for name in self.__output_type
            }
        return configured_infer_model.create_bindings(
            output_buffers=output_buffers
        )

    def start(self) -> None:
        """
        Start the Hailo handler by setting the stop event to False
        """
        self.__stop_event.clear()
        self.__logger.log("Hailo handler started.")

    def stop(self) -> None:
        """
        Stop the Hailo handler by setting the stop event.
        """
        self.__stop_event.set()
        self.__logger.log("Hailo handler stopped.")
