import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput

picam2 = Picamera2()
video_config = picam2.create_video_configuration()
picam2.configure(video_config)

encoder = H264Encoder()
output = FileOutput("video.h264")

picam2.start_recording(encoder, output)
print("Recording for 1 minute...")
time.sleep(60)  # Record for 60 seconds
picam2.stop_recording()
print("Recording stopped.")