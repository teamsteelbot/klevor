from http.server import HTTPServer

from . import StreamingServer

if __name__ == "__main__":
    with HTTPServer((StreamingServer.HOST, StreamingServer.PORT), StreamingServer) as server:
        print(f'Streaming on http://{StreamingServer.HOST}:{StreamingServer.PORT}/')
        server.serve_forever()