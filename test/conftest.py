import pytest
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')
        # log request
        print(f'Request: {self.command} {self.path}')

class StoppableHTTPServer(HTTPServer):
    def run(self):
        self.serve_forever()

    def stop(self):
        self.shutdown()

@pytest.fixture()
def port():
    return 8000

@pytest.fixture()
def http_server(port):
    server = StoppableHTTPServer(('', port), SimpleHTTPRequestHandler)
    server_thread = threading.Thread(target=server.run)
    server_thread.start()
    yield
    server.stop()
    server_thread.join()