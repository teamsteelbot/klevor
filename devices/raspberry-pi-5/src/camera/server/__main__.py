from http.server import HTTPServer

from .constants import HOST, PORT
from . import StreamingServer

if __name__ == "__main__":
    with HTTPServer((HOST, PORT), StreamingServer) as server:
        print(f'Streaming on http://{HOST}:{PORT}/')
        server.serve_forever()