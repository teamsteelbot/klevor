from http.server import HTTPServer

from . import StreamingServer
from .constants import HOST, PORT

if __name__ == "__main__":
	with HTTPServer((HOST, PORT), StreamingServer) as server:
		print(f'Streaming on http://{HOST}:{PORT}/')
		server.serve_forever()
