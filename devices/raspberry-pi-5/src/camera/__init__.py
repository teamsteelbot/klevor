import io
from multiprocessing import RLock, Queue, Event
from time import sleep
from typing import final

from PIL.Image import Image
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput

from ..constants import WIDTH, HEIGHT, IMAGE_FORMAT
from .constants import ADJUST_DURATION
from .abstracts import CameraABC
from ..log import Logger


class Camera(CameraABC):
    """
    Class implementation that wraps the functionality required for the Raspberry Pi Camera.
    """

    # Logger configuration
    LOGGER_TAG = "Camera"

    def __init__(self, writer_messages_queue: Queue, width: int = WIDTH, height: int = HEIGHT, rotation: int = 0, video_config: dict = None):
        """
        Initialize the camera with the specified width, height, and video configuration.

        Args:
            writer_messages_queue (Queue): Queue to hold log messages.
            width (int): Width of the camera image.
            height (int): Height of the camera image.
            video_config(dict): Configuration for video recording, if any.
            rotation (int): Rotation angle for the camera, default is 0.
        """
        # Initialize the logger
        self.__logger = Logger(writer_messages_queue, self.LOGGER_TAG)

        # Initialize the reentrant lock
        self.__rlock = RLock()

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

    @final
    def _start_preview(self) -> None:
        with self.__rlock:
            # Check if the preview is already started
            if self.__started_preview:
                return

            self.__picam2.start_preview()
            self.__started_preview = True

        # Log
        self.__logger.info("Camera preview started.") 

    @final
    def _stop_preview(self) -> None:
        with self.__rlock:
            # Check if the preview is running
            if not self.__started_preview:
                return

            self.__picam2.stop_preview()
            self.__started_preview = False

        # Log
        self.__logger.info("Camera preview stopped.") 

    @final
    def record_video(self, width: int = WIDTH, height: int = HEIGHT, duration: int = 10, file_path: str = 'video.h264',
                     encoder = H264Encoder()) -> None:
        with self.__rlock:
            # Stop the camera preview if it is running
            self._stop_preview()

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
        self.__logger.info(f"Video of {duration} seconds recording saved to {file_path}.") 

    @final
    def capture_image(self, adjust_duration: float = ADJUST_DURATION) -> Image:
        with self.__rlock:
            # Start the camera preview
            self._start_preview()

            # Allow time for the camera to adjust
            sleep(adjust_duration)

            # Capture the image
            image = self.__picam2.capture()

            # Stop the camera preview if required
            self._stop_preview()

        # Log
        self.__logger.info("Captured image.") 

        return image

    @final
    def capture_image_stream(self, image_format: str = IMAGE_FORMAT, adjust_duration: float = ADJUST_DURATION) -> io.BytesIO:
        with self.__rlock:
            # Start the camera preview
            self._start_preview()

            # Allow time for the camera to adjust
            sleep(adjust_duration)

            # Capture the image stream
            image_stream = io.BytesIO()
            self.__picam2.capture(image_stream, format=image_format)

            # Stop the camera preview
            self._stop_preview()

        # Log
        self.__logger.info("Captured image stream.") 

        return image_stream

    def __del__(self):
        """
        Destructor to clean up resources when the camera is no longer needed.
        """
        # Stop the camera preview
        self._stop_preview()

        # Stop the camera
        self.__picam2.close()

        # Log
        self.__logger.debug("Camera resources cleaned up.")
