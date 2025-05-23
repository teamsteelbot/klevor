import io
from multiprocessing import Lock

from PIL.Image import Image
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
from time import sleep

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
    __lock = None
    __picam2 = None
    __started_preview = False
    __config = None
    __video_config = None

    def __init__(self, width=WIDTH, height=HEIGHT, video_config=None):
        """
        Constructor.
        """
        # Initialize the lock
        self.__lock = Lock()

        # Configure the camera and video settings
        self.__picam2 = Picamera2()
        self.__config = self.__picam2.create_still_configuration(main={"size": (width, height)})
        self.__picam2.configure(self.__config)
        self.__video_config = video_config
        self.__started_preview = False

    def record_video(self, width=WIDTH, height=HEIGHT,duration=10, file_path='video.h264', encoder=H264Encoder()):
        """
        Record a video with the camera.
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
            print(f"Recording for {duration} seconds...")

            # Sleep for the duration of the recording
            sleep(duration)

            # Stop the recording
            self.__picam2.stop_recording()
            print("Recording stopped.")


    def capture_image(self, adjust_duration=DEFAULT_ADJUST_DURATION, stop_preview=False):
        """
        Capture an image with PyCamera2.
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

            # Return the image
            return image

    def capture_image_stream(self, adjust_duration=DEFAULT_ADJUST_DURATION, stop_preview=False, format=DEFAULT_FORMAT):
        """
        Capture an image stream.
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

            # Return the image stream
            return image_stream

    def capture_image_pil(self, adjust_duration=DEFAULT_ADJUST_DURATION, stop_preview=False) -> Image:
        """
        Capture an image and return a PIL image.
        """
        # Capture an image stream
        image_stream = self.capture_image_stream(adjust_duration, stop_preview)

        # Convert the image stream to a PIL image
        image_stream.seek(0)
        return Image.open(image_stream)

    def start_preview(self):
        """
        Start the camera preview.
        """
        with self.__lock:
            if not self.__started_preview:
                self.__picam2.start_preview()
                self.__started_preview = True
                print("Camera preview started.")

    def stop_preview(self):
        """
        Stop the camera preview.
        """
        with self.__lock:
            if self.__started_preview:
                self.__picam2.stop_preview()
                self.__started_preview = False
                print("Camera preview stopped.")

    def __del__(self):
        """
        Delete the camera object.
        """
        # Stop the camera preview
        if self.__started_preview:
            self.__picam2.stop_preview()

        # Stop the camera
        self.__picam2.close()
        print("Camera closed.")