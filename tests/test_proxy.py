import pytest
from tests.conftest import do_request

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