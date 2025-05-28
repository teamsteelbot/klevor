import shlex
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer


class StreamingHandler(BaseHTTPRequestHandler):
    """
    Streaming server for live video feed.
    """
    # Server configuration
    HOST = '0.0.0.0'
    PORT = 8080

    # Video configuration
    WIDTH = 640
    HEIGHT = 640
    FPS = 30
    CODEC = 'mjpeg'
    FORMAT = 'jpeg'

    @classmethod
    def generate_frames(cls):
        """
        Generate frames from the camera using libcamera-vid.
        """
        # Execute the libcamera-vid command to capture video
        command = f'libcamera-vid -n -t 0 --width {cls.WIDTH} --height {cls.HEIGHT} --framerate {cls.FPS} --codec {cls.CODEC} -o -'
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   bufsize=-1)

        try:
            while True:
                # Read the JPEG header (2 bytes)
                header = process.stdout.read(2)
                if not header:
                    print("No more data from libcamera-vid (header)")
                    break
                if header != b'\xff\xd8':
                    print(f"Incorrect JPEG SOI marker: {header}")
                    continue

                # Read the rest of the JPEG frame
                frame_data = header
                while True:
                    byte = process.stdout.read(1)
                    if not byte:
                        print("No more data from libcamera-vid (frame)")
                        break

                    frame_data += byte
                    if frame_data.endswith(b'\xff\xd9'):
                        print(f"Found complete JPEG frame, size: {len(frame_data)}")
                        yield (frame_data)
                        break
        finally:
            process.terminate()
            stderr_output = process.stderr.read().decode()
            if stderr_output:
                print(f"libcamera-vid stderr: {stderr_output}")

    def do_GET(self):
        """
        Handle GET requests for the streaming server.
        """
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(
                b'<html><head></head><body><h1>Live Stream</h1><img src="stream.mjpg" width="640" height="480" /></body></html>')
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            try:
                # Start generating frames
                for frame in self.generate_frames():
                    # Write the frame to the response
                    self.wfile.write(
                        b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                print(f"Error streaming: {e}")
        else:
            self.send_error(404)
            self.end_headers()


def main():
    """
    Main function to start the streaming server.
    """
    with HTTPServer((StreamingHandler.HOST, StreamingHandler.PORT), StreamingHandler) as server:
        print(f'Streaming on http://{StreamingHandler.HOST}:{StreamingHandler.PORT}/')
        server.serve_forever()


if __name__ == "__main__":
    main()
