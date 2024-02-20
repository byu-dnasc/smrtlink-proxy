import pytest
import http.client
import socket

def do_request(port):
    conn = http.client.HTTPConnection("localhost", port, timeout=2)
    try:
        try:
            conn.request("GET", "/")
        except ConnectionRefusedError:
            print("Connection refused, i.e. no server (or proxy) listening on that port.")
            return None
        return conn.getresponse()
    except http.client.HTTPException:
        print("HTTP exception occurred.")
        return None
    except socket.timeout:
        print("Socket timed out.")
        return None
    finally:
        conn.close()

@pytest.mark.parametrize("port", [8000])
def test_sanity(port, http_server):
    response = do_request(8000)
    assert response
    assert response.status == 200
    assert response.read() == b'Hello, world!'    

@pytest.mark.parametrize("port", [9091])
def test_proxy(port, http_server):
    response = do_request(9092)
    assert response