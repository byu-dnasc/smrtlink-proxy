from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import pytest

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

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

class AppRequestHandler(SimpleHTTPRequestHandler):
    log = []

class SLRequestHandler(SimpleHTTPRequestHandler):
    log = []

class StoppableHTTPServer(HTTPServer):

    def run(self):
        self.serve_forever()

    def stop(self):
        self.shutdown()

@pytest.fixture(autouse=True)
def app_log():
    yield AppRequestHandler.log
    AppRequestHandler.log.clear()

@pytest.fixture(autouse=True)
def sl_log():
    yield SLRequestHandler.log
    SLRequestHandler.log.clear()

@pytest.fixture()
def sl_server():
    server = StoppableHTTPServer(('localhost', 9091), SLRequestHandler)
    server_thread = threading.Thread(target=server.run)
    server_thread.start()
    yield
    server.stop()
    server_thread.join()

@pytest.fixture()
def app_server():
    app = StoppableHTTPServer(('localhost', 9093), AppRequestHandler)
    app_thread = threading.Thread(target=app.run)
    app_thread.start()
    yield
    app.stop()
    app_thread.join()