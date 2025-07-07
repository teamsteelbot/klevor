import io
from abc import ABC, abstractmethod

from PIL import ImageEnhance
from PIL.Image import Image

from .constants import ADJUST_DURATION
from ..constants import IMAGE_FORMAT
from ..log import Logger


class CameraABC(ABC):
    """
    Abstract class that wraps the functionality required for the Raspberry Pi Camera.
    """

    @staticmethod
    def convert_image_stream_to_pil(image_stream: io.BytesIO) -> Image:
        """
        Convert a byte stream to a PIL image.

        Args:
            image_stream (io.BytesIO): Byte stream containing the image data.
        Returns:
            Image: Converted PIL image.
        """
        # Convert the image stream to a PIL image
        image_stream.seek(0)
        return Image.open(image_stream)

    @property
    @abstractmethod
    def logger(self) -> Logger:
        """
        Get the logger instance for the Camera.

        Returns:
            Logger: The logger instance.
        """
        pass

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
    def capture_image_stream(
        self,
        image_format: str = IMAGE_FORMAT,
        adjust_duration: float = ADJUST_DURATION
    ) -> io.BytesIO:
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
    def record_video(
        self, width: int, height: int, duration: int,
        file_path: str, encoder
    ) -> None:
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
    def correct_color(
        image: Image,
        factor: float = 1.1
    ) -> Image:
        """
        Apply color correction to the image.

        Args:
            image (Image): The original image.
            factor (float): Factor by which to enhance the color balance.
        Returns:
            Image: Color-corrected image.
        """
        return ImageEnhance.Color(image).enhance(factor)


class PhotographerABC(ABC):
    """
    Abstract class to handle image processing for the camera.
    """

    @abstractmethod
    def logger(self) -> Logger:
        """
        Get the logger instance for the Photographer.

        Returns:
            Logger: The logger instance.
        """
        pass

    @abstractmethod
    def _start(self) -> None:
        """
        Start the photographer.

        Raises:
            RuntimeError: If the photographer fails to start.
        """
        pass

    @abstractmethod
    def _stop(self) -> None:
        """
        Stop the photographer.
        """
        pass

    @abstractmethod
    def _capture_image(self) -> None:
        """
        Capture an image from the camera and sends it to the corresponding queue.
        """
        pass

    @abstractmethod
    def run(self):
        """
        Loop to capture images and put them in the input photographer.
        """
        pass
