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

# make sure testing utilities (fixtures, etc.) are working
@pytest.mark.parametrize("server_port", [8000])
def test_testing_utilities(log):
    response = do_request(8000)
    assert response, 'Something wrong with http_server fixture.'
    assert response.status == 200
    assert response.body, 'Response body is missing.'
    assert len(log) != 0, 'Request was not logged.'

# make sure smrtlink-proxy is forwarding basic GET requests to the http_server fixture
# (smrtlink-proxy must be running)
@pytest.mark.parametrize("server_port", [9091])
def test_proxy():
    response = do_request(8088)
    assert response, 'Proxy server is not running.'
    response = do_request(9092)
    assert response, 'Proxy server is not forwarding requests.'
    assert response.status == 200
    assert response.body == 'Hello, world!', 'Response body is not coming through.'
