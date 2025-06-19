from threading import Thread
from multiprocessing import Event, Queue, RLock
from functools import partial
from hailo_platform import (HEF, VDevice,
                            FormatType, HailoSchedulingAlgorithm)
from typing import Callable, Optional, final
import os

from PIL.Image import Image
import cv2
import numpy as np

from .abstracts import HailoABC
from ...camera.image_processing_queue import ImageProcessingQueue
from ...log import LoggerABC
from ...log.sub_logger import SubLogger
from ..image_bounding_boxes import ImageBoundingBoxes
from ...utils import check_type
from .. import Yolo
from ..files import Files

class Hailo(HailoABC):
    """
    Class to handle Hailo inferences.
    """

    # Logger configuration
    LOG_TAG = "Hailo"

    # Image allowed extensions
    IMAGE_ALLOWED_EXTENSIONS: tuple = ('.jpg', '.png', '.bmp', '.jpeg')

    # Currently models file paths
    NO_PARKING_MODELS_NAME = [Yolo.MODEL_G, Yolo.MODEL_R]
    PARKING_MODELS_NAME = [Yolo.MODEL_M]

    # Batch size
    BATCH_SIZE = 1

    # Job timeout
    TIMEOUT = 10000

    def __init__(self, model_name: str, hef_file_path: str | os.PathLike[str], labels_path: str | os.PathLike[str], 
                 class_colors: tuple[tuple[int,int,int]], multi_threading: bool = True, multiprocessing: bool = False, 
                 image_processing_queue: ImageProcessingQueue = None, logger: Optional[LoggerABC] = None,
                 batch_size: int = BATCH_SIZE, input_type: Optional[str] = None,
                 output_type: Optional[dict[str, str]] = None,
                 put_output_inference_fn: Optional[Callable[[str, ImageBoundingBoxes], None]] = None) -> None:
        """
        Initialize the Hailo handler class.

        Args:
            model_name (str): Name of the YOLO model.
            hef_file_path (str | os.PathLike[str]): Path to the HEF file.
            labels_path (str | os.PathLike[str]): Path to the labels file.
            class_colors (tuple[tuple[int, int, int]]): Tuple mapping class IDs to RGB colors.
            multi_threading (bool): Whether to enable multi-threading. Defaults to True.
            multiprocessing (bool): Whether to enable multiprocessing. Defaults to False.
            image_processing_queue (ImageProcessingQueue): Queue for images. Defaults to None.
            logger (Optional[Logger]): Logger instance for logging messages. Defaults to None.
            batch_size (int): Batch size for inference. Defaults to BATCH_SIZE.
            input_type (Optional[str]): Format type of the input stream. Defaults to None.
            output_type (Optional[dict[str, str]]): Format type of the output stream. Defaults to None.
            put_output_inference_fn (Optional[Callable[[str, ImageBoundingBoxes], None]]): Function to put output inference results into the queue. Defaults to None.
        """
        # Initialize the reentrant lock
        self.__lock = RLock()

        # Check the type of model name
        check_type(model_name, str)
        self.__model_name = model_name

        # Check the HEF file path
        check_type(hef_file_path, str)
        Files.ensure_directory_exists(hef_file_path)
        self.__hef_file_path = hef_file_path

        # Check the labels path
        check_type(labels_path, str)
        Files.ensure_directory_exists(labels_path)
        self.__labels_path = labels_path

        # Load the labels
        self.__labels = Yolo.get_labels_from_txt(self.__labels_path)

        # Check the type of image processing queue
        check_type(image_processing_queue, ImageProcessingQueue)
        self.__images_queue = image_processing_queue

        # Check the type of logger
        check_type(logger, LoggerABC) if logger else None

        # Create a sub-logger for the Hailo handler
        self.__logger = SubLogger(logger, self.LOG_TAG) if logger else None

        # Check the type of class colors
        check_type(class_colors, dict)
        self.__class_colors = class_colors

        # Check the type of batch size
        check_type(batch_size, int)
        self.__batch_size = batch_size

        # Create the input queue
        self.__input_queue = Queue()

        # Create the stop event
        self.__stop_event = Event()
        self.__stop_event.set()  # Initially set to stop

        # Set the put output inference function
        self.__put_output_inference_fn = put_output_inference_fn

        # Initialize the thread
        self.__thread = None

        # Create the VDevice parameters
        params = VDevice.create_params()

        # Set the scheduling algorithm to round-robin to activate the scheduler
        params.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN

        # Set the group ID to SHARED
        if multi_threading or multiprocessing:
            params.group_id = "SHARED"

        # Enable multi-processing service
        if multiprocessing:
            params.multi_process_service = True

        # Set the VDevice parameters
        self.__target = VDevice(params)

        # Set the HEF model
        self.__hef = HEF(self.__hef_file_path)
        self.__infer_model = self.__target.create_infer_model(self.__hef_file_path)
        self.__infer_model.set_batch_size(batch_size)

        # Set the input and output types
        self._set_input_type(input_type) if input_type else None
        self._set_output_type(output_type) if output_type else None
        self.__output_type = output_type

    @final
    def _set_input_type(self, input_type: Optional[str] = None) -> None:
        self.__infer_model.input().set_format_type(getattr(FormatType, input_type))

    @final
    def _set_output_type(self, output_type_dict: Optional[dict[str, str]] = None) -> None:
        for output_name, output_type in output_type_dict.items():
            self.__infer_model.output(output_name).set_format_type(
                getattr(FormatType, output_type)
            )

    @final
    def _get_output_type_str(self, output_info) -> str | None:
        if not self.__output_type:
            return str(output_info.format.type).split(".")[1].lower()
        else:
            self.__output_type[output_info.name].lower()

    @final
    def get_input_shape(self) -> tuple[int, ...]:
        return self.__hef.get_input_vstream_infos()[0].shape  # Assumes one input

    @final
    def add_image(self, preprocessed_image: np.ndarray) -> None:
        # Check the type of preprocessed image
        check_type(preprocessed_image, np.ndarray)
        self.__input_queue.put(preprocessed_image)

    @final
    def _create_bindings(self, configured_infer_model) -> object:
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

    @final
    def _callback(
            self, completion_info, bindings, preprocessed_image: np.ndarray
    ) -> None:
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

    @final
    def _run(self) -> None:
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
                        self._callback,
                        preprocessed_image=preprocessed_image,
                        bindings=bindings
                    )
                )
            job.wait(self.TIMEOUT)  # Wait for the last job

    def __start(self) -> None:
        """
        Start the Hailo handler by setting the stop event to False
        """
        with self.__lock:
            # Clear the stop event to indicate that the handler is running
            self.__stop_event.clear()

    @final
    def is_running(self) -> bool:
        return not self.__stop_event.is_set()

    def __stop(self) -> None:
        """
        Stop the Hailo handler by setting the stop event to True.
        """
        with self.__lock:
            # Set the stop event to indicate that the handler should stop
            self.__stop_event.set()

    @final
    def is_stopped(self) -> bool:
        return not self.is_running()

    def start_thread(self) -> None:
        """
        Start the Hailo handler thread.
        """
        with self.__lock:
            if self.is_running():
                self.__logger.warning("Hailo handler thread is already running.") if self.__logger else None
                return

            # Start the Hailo handler
            self.__start()

            # Create and start the thread
            self.__thread = Thread(target=self._run)
            self.__thread.start()

        # Log
        self.__logger.info("Hailo handler thread started.") if self.__logger else None

    def stop_thread(self) -> None:
        """
        Stop the Hailo handler thread.
        """
        with self.__lock:
            if self.is_stopped():
                self.__logger.warning("Hailo handler thread is already stopped.") if self.__logger else None
                return

            # Stop the Hailo handler
            self.__stop()

            # Wait for the thread to finish
            self.__thread.join()
            self.__thread = None

        # Log
        self.__logger.info("Hailo handler thread stopped.") if self.__logger else None

    def __del__(self):
        """
        Destructor to ensure the thread is stopped when the object is deleted.
        """
        # Stop the thread if it is running
        self.stop_thread() if self.is_running() else None
        self.__logger.info("Hailo handler object deleted.") if self.__logger else None