from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import pytest
from requests import post, put, delete
import itertools

class UpstreamServer:

    def _get_handler(self):
        class RequestHandler(BaseHTTPRequestHandler):
            def log_request(inner_self, *args, **kwargs):
                self.request_flag = True
                super().log_request(*args, **kwargs)
        return RequestHandler

    def __init__(self, port):
        assert type(port) == int
        self.request_flag = False
        self.server = HTTPServer(('localhost', port), self._get_handler())
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()
    
    def stop(self):
        self.server.shutdown()
        self.server_thread.join()

    def request_logged(self):
        '''Get and reset the request flag.'''
        tmp = self.request_flag
        self.request_flag = False
        return tmp

GATEWAY_PROXY = "https://localhost:8244"
SERVICES_PROXY = "http://localhost:9092"
GATEWAY_PREFIX_1 = '/SMRTLink/1.0.0'
GATEWAY_PREFIX_2 = '/SMRTLink/2.0.0'
API = (
    (post, '/smrt-link/projects'),
    (put, '/smrt-link/projects/1'),
    (delete, '/smrt-link/projects/1'),
    (post, '/smrt-link/job-manager/jobs/analysis')
)

GATEWAY_API = itertools.chain(
    ((method, f'{GATEWAY_PROXY}{GATEWAY_PREFIX_1}{path}') for method, path in API),
    ((method, f'{GATEWAY_PROXY}{GATEWAY_PREFIX_2}{path}') for method, path in API)
)
SERVICES_API = ((method, f'{SERVICES_PROXY}{path}') for method, path in API)

@pytest.fixture(scope='module')
def app():
    app = UpstreamServer(9093)
    yield app
    app.stop()

@pytest.fixture(scope='module')
def sl_gateway():
    sl_gateway = UpstreamServer(8243)
    yield sl_gateway
    sl_gateway.stop()

@pytest.fixture(scope='module')
def sl_services():
    sl_services = UpstreamServer(9091)
    yield sl_services
    sl_services.stop()
   
@pytest.mark.parametrize('request_, uri', SERVICES_API)
def test_services_api(request_, uri, sl_services, app):
    request_(uri)
    assert sl_services.request_logged()
    assert app.request_logged()

@pytest.mark.parametrize('request_, uri', GATEWAY_API)
def test_gateway_api(request_, uri, sl_gateway, app):
    request_(uri, verify=False)
    assert sl_gateway.request_logged()
    assert app.request_logged()