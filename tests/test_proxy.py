import pytest
import http.client
import socket

class Response:
    def __init__(self, status, body):
        self.status = status
        self.body = body

def get_response(response):
    if not response:
        return None
    status = response.status
    body = response.read()
    if body:
        return Response(status, body.decode('utf-8'))
    else:
        return Response(status, None)

def do_request(port, method="GET", path="/"):
    try:
        conn = http.client.HTTPConnection("localhost", port, timeout=2)
        try:
            conn.request(method, path)
        except ConnectionRefusedError:
            print("Connection refused, i.e. no server (or proxy) listening on that port.")
            return None
        return get_response(conn.getresponse())        
    except http.client.HTTPException:
        print("HTTP exception occurred.")
        return None
    except socket.timeout:
        print("Socket timed out.")
        return None
    finally:
        conn.close()

sl_port = 9091
sl_proxy_port = 9092
proxy_home_port = 8088

# make sure testing utilities (fixtures, etc.) are working
@pytest.mark.usefixtures("sl_server")
def test_testing_utilities(sl_log):
    response = do_request(sl_port)
    assert response, 'Something wrong with http_server fixture.'
    assert response.status == 200
    assert response.body, 'Response body is missing.'
    assert len(sl_log) == 1, 'Request was not logged.'

# make sure smrtlink-proxy is forwarding GET requests to the sl_server fixture
# (smrtlink-proxy must be running)
@pytest.mark.usefixtures("sl_server")
def test_proxy():
    response = do_request(proxy_home_port)
    assert response, 'Proxy server is not running.'
    response = do_request(sl_proxy_port)
    assert response, 'Proxy server is not forwarding requests.'
    assert response.status == 200
    assert response.body == 'Hello, world!'

# request reaches both servers
@pytest.mark.usefixtures("sl_server", "app_server")
def test_request_mirroring(sl_log, app_log):
    sl_response = do_request(sl_proxy_port, method="POST", path="/smrt-link/projects")
    assert sl_response
    assert sl_response.status == 200
    assert sl_response.body == 'Hello, world!'
    assert len(sl_log) == 1
    assert len(app_log) == 1

# do not mirror get requests
@pytest.mark.usefixtures("sl_server", "app_server")
def test_request_mirroring_fail(sl_log, app_log):
    sl_response = do_request(sl_proxy_port, method="GET", path="/smrt-link/projects")
    assert sl_response
    assert sl_response.status == 200
    assert sl_response.body == 'Hello, world!'
    assert len(sl_log) == 1
    assert len(app_log) == 0