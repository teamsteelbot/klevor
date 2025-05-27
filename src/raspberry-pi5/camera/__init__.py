import io
from multiprocessing import Lock

from PIL.Image import Image
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
from time import sleep

from log import Logger

# Camera settings
WIDTH=640
HEIGHT=640
FPS=30
DEFAULT_CODEC= 'mjpeg'
DEFAULT_FORMAT = 'jpeg'
DEFAULT_ADJUST_DURATION=0.02

# Server settings
SERVER_PORT=8080

class Camera:
    """
    Class that wraps the functionality required for the Raspberry Pi Camera.
    """
    __log_tag = "Camera"
    __logger = None
    __lock = None
    __picam2 = None
    __started_preview = False
    __config = None
    __video_config = None

    def __init__(self, logger: Logger, width=WIDTH, height=HEIGHT, video_config=None):
        """
        Initialize the camera with the specified width, height, and video configuration.

        Args:
            logger (Logger): Logger instance for logging messages.
            width (int): Width of the camera image.
            height (int): Height of the camera image.
            video_config: Configuration for video recording, if any.
        """
        # Initialize the lock
        self.__lock = Lock()

        # Check the type of logger
        if not isinstance(logger, Logger):
            raise ValueError("logger must be an instance of Logger")

        # Get the sub-logger for this class
        self.__logger = logger.get_sub_logger(self.__log_tag)

        # Log
        self.__logger.log("Initializing camera...")

        # Configure the camera and video settings
        self.__picam2 = Picamera2()
        self.__config = self.__picam2.create_still_configuration(main={"size": (width, height)})
        self.__picam2.configure(self.__config)
        self.__video_config = video_config
        self.__started_preview = False

    def record_video(self, width=WIDTH, height=HEIGHT,duration=10, file_path='video.h264', encoder=H264Encoder()) -> None:
        """
        Record a video with the camera.

        Args:
            width (int): Width of the video.
            height (int): Height of the video.
            duration (int): Duration of the video in seconds.
            file_path (str): Path to save the recorded video file.
            encoder: Encoder to use for video recording, default is H264Encoder.
        """
        with self.__lock:
            # Stop the camera preview if it is running
            if self.__started_preview:
                self.__picam2.stop_preview()
                self.__started_preview = False

            # Configure the camera for video recording
            if self.__video_config is None:
                self.__video_config = self.__picam2.create_video_configuration(main={"size": (width, height)}, display="preview")
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
        self.__logger.log(f"Video of {duration} seconds recording saved to {file_path}.")

    def capture_image(self, adjust_duration=DEFAULT_ADJUST_DURATION, stop_preview=False) -> Image:
        """
        Capture an image with PiCamera2.

        Args:
            adjust_duration (float): Duration to allow the camera to adjust before capturing the image.
            stop_preview (bool): Whether to stop the camera preview after capturing the image.
        Returns:
            Image: Captured image.
        """
        with self.__lock:
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
        self.__logger.log("Captured image.")

        return image

    def capture_image_stream(self, adjust_duration=DEFAULT_ADJUST_DURATION, stop_preview=False, format=DEFAULT_FORMAT) -> io.BytesIO:
        """
        Capture an image stream.

        Args:
            adjust_duration (float): Duration to allow the camera to adjust before capturing the image.
            stop_preview (bool): Whether to stop the camera preview after capturing the image.
            format (str): Format of the captured image stream, default is 'jpeg'.
        Returns:
            io.BytesIO: Image stream in bytes.
        """
        with self.__lock:
            # Start the camera preview
            if not self.__started_preview:
                self.__picam2.start_preview()
                self.__started_preview = True

            # Allow time for the camera to adjust
            sleep(adjust_duration)

            # Capture the image stream
            image_stream = io.BytesIO()
            self.__picam2.capture(image_stream, format=format)

            # Stop the camera preview if required
            if stop_preview:
                self.__picam2.stop_preview()
                self.__started_preview = False

        # Log
        self.__logger.log("Captured image stream.")

        return image_stream

    def capture_image_pil(self, adjust_duration=DEFAULT_ADJUST_DURATION, stop_preview=False) -> Image:
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

    def start_preview(self)->None:
        """
        Start the camera preview.
        """
        with self.__lock:
            # Check if the preview is already started
            if not self.__started_preview:
                self.__picam2.start_preview()
                self.__started_preview = True

        # Log
        self.__logger.log("Camera preview started.")

    def stop_preview(self)->None:
        """
        Stop the camera preview.
        """
        with self.__lock:
            # Check if the preview is running
            if self.__started_preview:
                self.__picam2.stop_preview()
                self.__started_preview = False

        # Log
        self.__logger.log("Camera preview stopped.")

    def __del__(self):
        """
        Delete the camera object.
        """
        # Stop the camera preview
        self.stop_preview()

        # Stop the camera
        self.__picam2.close()

        # Log
        self.__logger.log("Closed camera.")