from abc import ABC, abstractmethod
from typing import Optional

from PIL.Image import Image
import numpy as np

class HailoABC(ABC):
    """
    Abstract base class for Hailo handlers.
    """

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
    def _set_output_type(self, output_type_dict: Optional[dict[str, str]] = None) -> None:
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

    @classmethod
    @abstractmethod
    def preprocess(cls, image: Image, width: int = Preprocessing.WIDTH, height: int = Preprocessing.HEIGHT) -> np.ndarray:
        """
        Resize image with unchanged aspect ratio using padding.

        Args:
            image (Image): Input image.
            width (int): Model input width.
            height (int): Model input height.

        Returns:
            np.ndarray: Preprocessed and padded image.
        """
        pass

    @abstractmethod
    def put_image(self, preprocessed_image: np.ndarray) -> None:
        """
        Put a preprocessed image into the input queue.

        Args:
            preprocessed_image (np.ndarray): Preprocessed image to be put into the queue.
        """
        pass

    @abstractmethod
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
    def start(self) -> None:
        """
        Start the Hailo handler by setting the stop event to False
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Stop the Hailo handler by setting the stop event.
        """
        pass