from abc import ABC, abstractmethod
import io
from typing import Callable

import numpy as np
from PIL import ImageEnhance
from PIL.Image import Image

from .constants import ADJUST_DURATION
from ..model import ImageBoundingBoxes

class CameraABC(ABC):
    """
    Abstract class that wraps the functionality required for the Raspberry Pi Camera.
    """

    @abstractmethod
    def _start_preview(self) -> None:
        """
        Start the camera preview.
        """
        pass

    @abstractmethod
    def _stop_preview(self) -> None:
        """
        Stop the camera preview.
        """
        pass

    @abstractmethod
    def capture_image_pil(self, adjust_duration: float = ADJUST_DURATION) -> Image:
        """
        Capture an image and return a PIL image.

        Args:
            adjust_duration (float): Duration to allow the camera to adjust before capturing the image.
        Returns:
            Image: Captured image as a PIL Image.
        """
        pass

    @abstractmethod
    def capture_image_stream(self, image_format: str, adjust_duration: float = 0) -> io.BytesIO:
        """
        Capture an image and return a byte stream.

        Args:
            image_format (str): Format of the image to be captured.
            adjust_duration (float): Duration to allow the camera to adjust before capturing the image.
        Returns:
            io.BytesIO: Captured image as a byte stream.
        """
        pass

    @abstractmethod
    def record_video(self, width: int, height: int, duration: int, file_path: str, encoder) -> None:
        """
        Record a video with the camera.

        Args:
            width (int): Width of the video.
            height (int): Height of the video.
            duration (int): Duration of the video in seconds.
            file_path (str): Path to save the recorded video file.
            encoder: Encoder to use for video recording.
        """
        pass

    @staticmethod
    def correct_color(image: Image, factor: float = 1.1) -> Image:
        """
        Apply color correction to the image.

        Args:
            image (Image): The original image.
            factor (float): Factor by which to enhance the color balance.
        Returns:
            Image: Color-corrected image.
        """
        return ImageEnhance.Color(image).enhance(factor)

class ImageProcessingQueueABC(ABC):
    """
    Abstract class for managing a queue of images for processing in a real-time tracking system.
    """

    @abstractmethod
    def is_running(self) -> bool:
        """
        Check if the image processing queue is running.

        Returns:
            bool: True if the image processing queue is running, False otherwise.
        """
        pass

    @abstractmethod
    def is_stopped(self) -> bool:
        """
        Check if the image processing queue is stopped.

        Returns:
            bool: True if the image processing queue is not running, False otherwise.
        """
        pass

    @abstractmethod
    def add_image(self, image: Image) -> None:
        """
        Put image in input images queue.

        Args:
            image (Image): Image to put in the input images queue.
        """
        pass

    @abstractmethod
    def get_image(self, preprocess_fn: Callable[[Image], np.ndarray]) -> np.ndarray | None:
        """
        Get image from input images queue.

        Returns:
            np.ndarray|None: Preprocessed image from the input images queue or None if no image is available.
        """
        pass

    @abstractmethod
    def add_inference(self, model_name: str, inference: ImageBoundingBoxes) -> None:
        """
        Put inference in output inference queue.

        Args:
            model_name (str): Name of the model that produced the inference.
            inference (ImageBoundingBoxes): Inference to put in the output inference queue.
        """
        pass

    @abstractmethod
    def get_inference(self) -> tuple[str, ImageBoundingBoxes] | None:
        """
        Get inference from output inference queue.

        Returns:
            tuple[str, ImageBoundingBoxes]|None: Tuple containing model name and inference from the output inference queue or None if no inference is available.
        """
        pass

    @abstractmethod
    def capture_image(self) -> None:
        """
        Capture image from camera.
        """
        pass

    @abstractmethod
    def wait_capture_image_event(self) -> None:
        """
        Wait for the capture image event to be set.
        """
        pass

    @abstractmethod
    def set_capture_image_event(self) -> None:
        """
        Set the capture image event.
        """
        pass

    @abstractmethod
    def wait_pending_input_image_event(self) -> None:
        """
        Wait for the pending input image event to be set.
        """
        pass

    @abstractmethod
    def wait_pending_output_inference_event(self) -> None:
        """
        Wait for the pending output inference event to be set.
        """
        pass

    @abstractmethod
    def _loop(self):
        """
        Loop to capture images and put them in the input image processing queue.
        """
        pass

    @abstractmethod
    def start_thread(self) -> None:
        """
        Start the image processing queue thread.
        """
        pass

    @abstractmethod
    def stop_thread(self) -> None:
        """
        Stop the image processing queue thread.
        """
        pass