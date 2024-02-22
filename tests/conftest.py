from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import pytest

log_list = [] # shared state cleared by fixture after each test

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    log = log_list

    def _log_request(self):
        body = None
        if 'Content-Length' in self.headers:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
        self.log.append(f'Method: {self.command}, URI: {self.path}, Body: {body}')

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')
        self._log_request()

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')
        self._log_request()

class StoppableHTTPServer(HTTPServer):

    def run(self):
        self.serve_forever()

    def stop(self):
        self.shutdown()

@pytest.fixture(autouse=True)
def server_port():
    return 8000

@pytest.fixture(autouse=True)
def log():
    yield log_list
    log_list.clear()

@pytest.fixture(autouse=True)
def http_server(server_port):
    server = StoppableHTTPServer(('localhost', server_port), SimpleHTTPRequestHandler)
    server_thread = threading.Thread(target=server.run)
    server_thread.start()
    yield
    server.stop()
    server_thread.join()