import os
from functools import partial
from queue import Empty
from multiprocessing import Event, Queue, RLock
from multiprocessing.synchronize import Event as EventCls
from typing import Optional, final

import cv2
import numpy as np
from PIL.Image import Image
from hailo_platform import (FormatType, HEF, HailoSchedulingAlgorithm, VDevice)

from .abstracts import HailoABC
from ..constants import MODEL_G, MODEL_M, MODEL_R
from ..files import Files
from ..log import Logger
from ..model import ImageBoundingBoxes
from ..utils import is_instance
from ..utils.decorators import ignore_sigint
from ..log.decorators import log_on_error


class Hailo(HailoABC):
    """
    Class to handle Hailo inferences.
    """

    # Logger configuration
    LOGGER_TAG = "Hailo"

    # Image allowed extensions
    IMAGE_ALLOWED_EXTENSIONS: tuple = ('.jpg', '.png', '.bmp', '.jpeg')

    # Currently models file paths
    NO_PARKING_MODELS_NAME = [MODEL_G, MODEL_R]
    PARKING_MODELS_NAME = [MODEL_M]

    # Batch size
    BATCH_SIZE = 1

    # Wait timeout
    WAIT_TIMEOUT = 0.1

    # Job timeout
    JOB_TIMEOUT = 5000

    def __init__(
        self,
        model_name: str,
        hef_file_path: str | os.PathLike[str],
        labels_path: str | os.PathLike[str],
        class_colors: tuple[tuple[int, int, int]],
        processed_images_queue: Queue,
        inferences_queue: Queue,
        stop_event: EventCls,
        writer_messages_queue: Queue,
        multi_threading: bool = True,
        multiprocessing: bool = False,
        batch_size: int = BATCH_SIZE,
        input_type: Optional[str] = None,
        output_type: Optional[dict[str, str]] = None
    ) -> None:
        """
        Initialize the Hailo handler class.

        Args:
            model_name (str): Name of the YOLO model.
            hef_file_path (str | os.PathLike[str]): Path to the HEF file.
            labels_path (str | os.PathLike[str]): Path to the labels file.
            class_colors (tuple[tuple[int, int, int]]): Tuple mapping class IDs to RGB colors.
            processed_images_queue (Queue): Queue to hold input images for processing.
            inferences_queue (Queue): Queue to hold the inferences from the Hailo handlers.
            stop_event (EventCls): Event to signal when the Hailo handler should stop.
            writer_messages_queue (Queue): Queue to hold log messages.
            multi_threading (bool): Whether to enable multi-threading.
            multiprocessing (bool): Whether to enable multiprocessing.
            batch_size (int): Batch size for inference.
            input_type (Optional[str]): Format type of the input stream.
            output_type (Optional[dict[str, str]]): Format type of the output stream.
        """
        # Initialize the queues and events
        self.__processed_images_queue = processed_images_queue
        self.__inferences_queue = inferences_queue
        self.__started_event = Event()
        self.__stop_event = stop_event

        # Initialize the logger
        self.__logger_tag = f"{self.LOGGER_TAG}_{model_name}"
        self.__logger = Logger(writer_messages_queue, self.__logger_tag)

        # Initialize the reentrant lock
        self.__rlock = RLock()

        # Check the type of model name
        is_instance(model_name, str)
        self.__model_name = model_name

        # Check the HEF file path
        is_instance(hef_file_path, str)
        Files.ensure_directory_exists(hef_file_path)
        self.__hef_file_path = hef_file_path

        # Check the labels path
        is_instance(labels_path, str)
        Files.ensure_directory_exists(labels_path)
        self.__labels = Files.get_labels_from_txt(labels_path)

        # Check the type of class colors
        is_instance(class_colors, dict)
        self.__class_colors = class_colors

        # Check the type of batch size
        is_instance(batch_size, int)
        self.__batch_size = batch_size

        # Initialize the multiprocessing and multi-threading flags
        is_instance(multi_threading, bool)
        self.__multi_threading = multi_threading
        is_instance(multiprocessing, bool)
        self.__multiprocessing = multiprocessing

        # Initialize the input type
        is_instance(input_type, (str, type(None)))
        self.__input_type = input_type

        # Initialize the output type
        self.__output_type: Optional[dict[str, str]] = output_type

        # Initialize the target, HEF, and infer model
        self.__target = None
        self.__hef = None
        self.__infer_model = None

    @final
    def logger(self) -> Logger:
        return self.__logger

    @final
    def _set_input_type(self, input_type: Optional[str] = None) -> None:
        self.__infer_model.input().set_format_type(
            getattr(FormatType, input_type)
        )

    @final
    def _set_output_type(
        self, output_type_dict: Optional[
            dict[str, str]] = None
    ) -> None:
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
        # Assumes one input
        return self.__hef.get_input_vstream_infos()[0].shape

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
        self.__inferences_queue.put(ImageBoundingBoxes.from_hailo(result))

    @final
    @ignore_sigint
    @log_on_error()
    def run(self) -> None:
        with self.__rlock:
            # Check if the stop event is set
            if self.__stop_event.is_set():
                self.__logger.warning(
                    f"Stop event is set. Hailo handler for model '{self.__model_name}' will not run."
                )
                return

            # Check if the Hailo handler for the given model name is already running
            if self.__started_event.is_set():
                self.__logger.warning(
                    f"Hailo handler for model '{self.__model_name}' is already running. Cannot start again."
                )
                return

            # Set the started event to signal that the Hailo handler has started
            self.__started_event.set()

        # Create the VDevice parameters
        params = VDevice.create_params()

        # Set the scheduling algorithm to round-robin to activate the scheduler
        params.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN

        # Set the group ID to SHARED
        if self.__multi_threading or self.__multiprocessing:
            params.group_id = "SHARED"

        # Enable multi-processing service
        if self.__multiprocessing:
            params.multi_process_service = True

        # Set the VDevice parameters
        self.__target = VDevice(params)

        # Set the HEF model
        self.__hef = HEF(self.__hef_file_path)
        self.__infer_model = self.__target.create_infer_model(
            self.__hef_file_path
        )
        self.__infer_model.set_batch_size(self.__batch_size)

        # Set the input and output types
        self._set_input_type(self.__input_type) if self.__input_type else None
        self._set_output_type(
            self.__output_type
        ) if self.__output_type else None

        with self.__infer_model.configure() as configured_infer_model:
            while self.is_running():
                try:
                    # Get a preprocessed image from the input queue
                    preprocessed_image = self.__processed_images_queue.get(
                        timeout=self.WAIT_TIMEOUT
                    )

                except Empty:
                    # If the queue is empty, continue to the next iteration
                    continue

                # Create the bindings for the input and output buffers
                bindings = self._create_bindings(configured_infer_model)
                bindings.input().set_buffer(np.array(preprocessed_image))

                configured_infer_model.wait_for_async_ready(
                    timeout_ms=self.JOB_TIMEOUT
                )
                job = configured_infer_model.run_async(
                    bindings, partial(
                        self._callback,
                        preprocessed_image=preprocessed_image,
                        bindings=bindings
                    )
                )

            # Wait for the last job
            job.wait(self.JOB_TIMEOUT)

        # Clear the started event
        with self.__rlock:
            self.__started_event.clear()

    @final
    def is_running(self) -> bool:
        return not self.__stop_event.is_set()

    @final
    def is_stopped(self) -> bool:
        return not self.is_running()

    def __del__(self):
        """
        Destructor to clean up resources when the Hailo handler is no longer needed.
        """
        self.__stop_event.set()

        # Log
        self.__logger.debug(
            f"Hailo handler instance for model '{self.__model_name}' is being deleted. Resources will be cleaned up."
        )
