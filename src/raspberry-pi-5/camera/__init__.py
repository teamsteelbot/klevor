import io
from multiprocessing import RLock
from time import sleep
from typing import Optional

from PIL import ImageEnhance
from PIL.Image import Image
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput

from log import Logger
from log.sub_logger import SubLogger
from utils import check_type


class Camera:
    """
    Class that wraps the functionality required for the Raspberry Pi Camera.
    """
    # Logger configuration
    LOG_TAG = "Camera"

    # Camera settings
    WIDTH = 640
    HEIGHT = 640
    FORMAT = 'jpeg'
    ADJUST_DURATION = 0.02

    def __init__(self, logger: Optional[Logger] = None, width: int = WIDTH, height: int = HEIGHT, rotation: int = 0, video_config: dict = None):
        """
        Initialize the camera with the specified width, height, and video configuration.

        Args:
            logger (Optional[Logger]): Logger instance for logging messages.
            width (int): Width of the camera image.
            height (int): Height of the camera image.
            video_config(dict): Configuration for video recording, if any.
            rotation (int): Rotation angle for the camera, default is 0.
        """
        # Initialize the reentrant lock
        self.__rlock = RLock()

        # Check the type of logger
        check_type(logger, Logger) if logger else None

        # Get the sub-logger for this class
        self.__logger = SubLogger(logger, self.LOG_TAG) if logger else None

        # Log
        self.__logger.debug("Initializing camera...") if self.__logger else None

        # Configure the camera and video settings
        self.__picam2 = Picamera2()
        self.__picam2.set_controls({"AwbMode": "auto"})  # Set Auto White Balance (AWB)
        self.__config = self.__picam2.create_still_configuration(main={"size": (width, height)})
        self.__picam2.configure(self.__config)

        # Configure rotation if specified
        if rotation:
            self.__picam2.set_controls({"Rotation": rotation})

        # Set the video configuration if provided and the started preview flag
        self.__video_config = video_config
        self.__started_preview = False

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

    def record_video(self, width: int = WIDTH, height: int = HEIGHT, duration: int = 10, file_path: str = 'video.h264',
                     encoder = H264Encoder()) -> None:
        """
        Record a video with the camera.

        Args:
            width (int): Width of the video.
            height (int): Height of the video.
            duration (int): Duration of the video in seconds.
            file_path (str): Path to save the recorded video file.
            encoder: Encoder to use for video recording, default is H264Encoder.
        """
        with self.__rlock:
            # Stop the camera preview if it is running
            if self.__started_preview:
                self.__picam2.stop_preview()
                self.__started_preview = False

            # Configure the camera for video recording
            if not self.__video_config:
                self.__video_config = self.__picam2.create_video_configuration(main={"size": (width, height)},
                                                                               display="preview")
            self.__picam2.configure(self.__video_config)

            # Get the  output
            output = FileOutput(file_path)

            # Start the recording
            self.__picam2.start_recording(encoder, output)

            # Sleep for the duration of the recording
            sleep(duration)

            # Stop the recording
            self.__picam2.stop_recording()

        # Log
        self.__logger.info(f"Video of {duration} seconds recording saved to {file_path}.") if self.__logger else None

    def capture_image(self, adjust_duration: float = ADJUST_DURATION, stop_preview: bool = False) -> Image:
        """
        Capture an image with PiCamera2.

        Args:
            adjust_duration (float): Duration to allow the camera to adjust before capturing the image.
            stop_preview (bool): Whether to stop the camera preview after capturing the image.
        Returns:
            Image: Captured image.
        """
        with self.__rlock:
            # Start the camera preview
            if not self.__started_preview:
                self.__picam2.start_preview()
                self.__started_preview = True

            # Allow time for the camera to adjust
            sleep(adjust_duration)

            # Capture the image
            image = self.__picam2.capture()

            # Stop the camera preview if required
            if stop_preview:
                self.__picam2.stop_preview()
                self.__started_preview = False

        # Log
        self.__logger.info("Captured image.") if self.__logger else None

        return image

    def capture_image_stream(self, adjust_duration: float = ADJUST_DURATION, stop_preview: bool = False, image_format: str = FORMAT) -> io.BytesIO:
        """
        Capture an image stream.

        Args:
            adjust_duration (float): Duration to allow the camera to adjust before capturing the image.
            stop_preview (bool): Whether to stop the camera preview after capturing the image.
            image_format (str): Format of the captured image stream, default is 'jpeg'.
        Returns:
            io.BytesIO: Image stream in bytes.
        """
        with self.__rlock:
            # Start the camera preview
            if not self.__started_preview:
                self.__picam2.start_preview()
                self.__started_preview = True

            # Allow time for the camera to adjust
            sleep(adjust_duration)

            # Capture the image stream
            image_stream = io.BytesIO()
            self.__picam2.capture(image_stream, format=image_format)

            # Stop the camera preview if required
            if stop_preview:
                self.__picam2.stop_preview()
                self.__started_preview = False

        # Log
        self.__logger.info("Captured image stream.") if self.__logger else None

        return image_stream

    def capture_image_pil(self, adjust_duration: float = ADJUST_DURATION, stop_preview: bool = False) -> Image:
        """
        Capture an image and return a PIL image.

        Args:
            adjust_duration (float): Duration to allow the camera to adjust before capturing the image.
            stop_preview (bool): Whether to stop the camera preview after capturing the image.
        Returns:
            Image: Captured image as a PIL Image.
        """
        # Capture an image stream
        image_stream = self.capture_image_stream(adjust_duration, stop_preview)

        # Convert the image stream to a PIL image
        image_stream.seek(0)
        return Image.open(image_stream)

    def start_preview(self) -> None:
        """
        Start the camera preview.
        """
        with self.__rlock:
            # Check if the preview is already started
            if not self.__started_preview:
                self.__picam2.start_preview()
                self.__started_preview = True

        # Log
        self.__logger.info("Camera preview started.") if self.__logger else None

    def stop_preview(self) -> None:
        """
        Stop the camera preview.
        """
        with self.__rlock:
            # Check if the preview is running
            if self.__started_preview:
                self.__picam2.stop_preview()
                self.__started_preview = False

        # Log
        self.__logger.info("Camera preview stopped.") if self.__logger else None

    def __del__(self):
        """
        Delete the camera object.
        """
        # Stop the camera preview
        self.stop_preview()

        # Stop the camera
        self.__picam2.close()

        # Log
        self.__logger.info("Closed camera.") if self.__logger else None
