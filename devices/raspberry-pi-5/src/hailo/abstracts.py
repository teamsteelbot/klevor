from abc import ABC, abstractmethod
from typing import Optional

import cv2
import numpy as np
from PIL.Image import Image

from ..constants import WIDTH, HEIGHT
from ..opencv.constants import PADDING_COLOR


class HailoABC(ABC):
    """
    Abstract base class for Hailo handlers.
    """

    @staticmethod
    def preprocess(image: Image, width: int = WIDTH,
                   height: int = HEIGHT) -> np.ndarray:
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
        new_img_width, new_img_height = int(img_width * scale), int(
            img_height * scale)
        image = cv2.resize(image, (new_img_width, new_img_height),
                           interpolation=cv2.INTER_CUBIC)

        # Calculate padding and create padded image
        padded_image = np.full((height, width, 3), PADDING_COLOR,
                               dtype=np.uint8)
        x_offset = (height - new_img_width) // 2
        y_offset = (height - new_img_height) // 2
        padded_image[y_offset:y_offset + new_img_height,
        x_offset:x_offset + new_img_width] = image
        return padded_image

    @abstractmethod
    def _set_input_type(self, input_type: Optional[str] = None) -> None:
        """
        Set the input type for the HEF model. If the model has multiple inputs,
        it will set the same type of all of them.

        Args:
            input_type (Optional[str]): Format type of the input stream.
        """
        pass

    @abstractmethod
    def _set_output_type(self, output_type_dict: Optional[
        dict[str, str]] = None) -> None:
        """
        Set the output type for the HEF model. If the model has multiple outputs,
        it will set the same type for all of them.

        Args:
            output_type_dict (Optional[dict[str, str]]): Format type of the output stream.
        """
        pass

    @abstractmethod
    def _get_output_type_str(self, output_info) -> str | None:
        """
        Get the output type string for the HEF model.

        Args:
            output_info: Information about the output stream.
        """
        pass

    @abstractmethod
    def get_input_shape(self) -> tuple[int, ...]:
        """
        Get the shape of the model's input layer.

        Returns:
            tuple[int, ...]: Shape of the model's input layer.
        """
        pass

    @abstractmethod
    def _create_bindings(self, configured_infer_model) -> object:
        """
        Create bindings for input and output buffers.

        Args:
            configured_infer_model: The configured inference model.

        Returns:
            object: Bindings object with input and output buffers.
        """
        pass

    @abstractmethod
    def _callback(
            self, completion_info, bindings, preprocessed_image: np.ndarray
    ) -> None:
        """
        Callback function for handling inference results.

        Args:
            completion_info: Information about the completion of the inference task.
            bindings: Binding objects containing input and output buffers.
            preprocessed_image (np.ndarray): Preprocessed image used for inference.
        """
        pass

    @abstractmethod
    def run(self) -> None:
        """
        Run the inference loop.

        This method continuously retrieves batches of images from the input queue,
        preprocesses them, and runs inference using the configured infer model.
        """
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """
        Check if the Hailo handler is running.

        Returns:
            True if the handler is running, False otherwise.
        """
        pass

    @abstractmethod
    def is_stopped(self) -> bool:
        """
        Check if the Hailo handler is stopped.

        Returns:
            True if the handler is stopped, False otherwise.
        """
        pass


class ObjectDetectorABC(ABC):
    """
    Abstract class to handle object detection using Hailo handlers.
    """

    @abstractmethod
    def is_running(self) -> bool:
        """
        Check if the object detection is running.

        Returns:
            bool: True if running, False otherwise.
        """
        pass

    @abstractmethod
    def is_stopped(self) -> bool:
        """
        Check if the object detection is stopped.

        Returns:
            bool: True if stopped, False otherwise.
        """
        pass

    @abstractmethod
    def run(self) -> None:
        """
        The main loop to run the object detection using Hailo handlers.
        """
        pass
