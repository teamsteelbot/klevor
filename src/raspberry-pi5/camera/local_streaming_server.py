from http.server import BaseHTTPRequestHandler, HTTPServer

from camera import SERVER_PORT
from camera.frames import generate_frames

# Streaming server for live video feed
class StreamingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
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
                for frame in generate_frames():
                    # Write the frame to the response
                    self.wfile.write(
                        b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                print(f"Error streaming: {e}")
        else:
            self.send_error(404)
            self.end_headers()

if __name__ == "__main__":
    with HTTPServer(('0.0.0.0', SERVER_PORT), StreamingHandler) as server:
        print(f'Streaming on http://localhost:{SERVER_PORT}/')
        server.serve_forever()