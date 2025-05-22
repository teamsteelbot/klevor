import io
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
DEFAULT_ADJUST_DURATION=2

# Server settings
SERVER_PORT=8080

# Class that wraps the functionality required for the Raspberry Pi Camera
class Camera:
    __picam2 = None
    __config = None
    __preview_state = None

    # Constructor
    def __init__(self, width=WIDTH, height=HEIGHT):
        # Configure the camera globally
        self.__picam2 = Picamera2()
        self.__config = self.__picam2.create_still_configuration(main={"size": (width, height)})
        self.__picam2.configure(self.__config)
        self.__picam2.start()

    # Capture a video
    def record_video(self, duration=10, file_path='video.h264', encoder=H264Encoder()):
        # Configure the camera for video recording
        video_config = self.__picam2.create_video_configuration()
        self.__picam2.configure(video_config)

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

    # Set camera as preview
    def start_preview(self):
        if self.__preview_state is None:
            self.__picam2.start_preview()
            self.__preview_state = True
        else:
            print("Preview already started.")

    # Stop camera preview
    def stop_preview(self):
        if self.__preview_state is not None:
            self.__picam2.stop_preview()
            self.__preview_state = None
        else:
            print("Preview already stopped.")


    # Capture an image with pycamera
    def capture_image(self, adjust_duration=DEFAULT_ADJUST_DURATION, stop_preview=False):
        # Start the camera preview
        self.start_preview()

        # Allow time for the camera to adjust
        sleep(adjust_duration)

        # Capture the image
        image = self.__picam2.capture()

        # Stop the camera preview if required
        if stop_preview:
            self.stop_preview()

        # Return the image
        return image

    # Capture a image stream
    def capture_image_stream(self, adjust_duration=DEFAULT_ADJUST_DURATION, stop_preview=False, format=DEFAULT_FORMAT):
        # Start the camera preview
        self.start_preview()

        # Allow time for the camera to adjust
        sleep(adjust_duration)

        # Capture the image stream
        image_stream = io.BytesIO()
        self.__picam2.capture(image_stream, format=format)

        # Stop the camera preview if required
        if stop_preview:
            self.stop_preview()

        # Return the image stream
        return image_stream

    # Delete
    def __del__(self):
        # Stop the camera preview
        if self.__preview_state is not None:
            self.stop_preview()

        # Stop the camera
        self.__picam2.close()
        print("Camera closed.")