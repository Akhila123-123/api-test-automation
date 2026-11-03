import os
import threading
import time
from http.server import ThreadingHTTPServer

import pytest
import requests

import mock_api

# By default the suite starts the local mock API. To test a real API instead,
# set BASE_URL, e.g.  BASE_URL=https://jsonplaceholder.typicode.com pytest
# (note: write tests such as DELETE only make sense against the mock API).


@pytest.fixture(scope="session")
def base_url():
    external = os.environ.get("BASE_URL")
    if external:
        yield external.rstrip("/")
        return
    server = ThreadingHTTPServer(("127.0.0.1", 0), mock_api.Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.1)
    yield f"http://127.0.0.1:{port}"
    server.shutdown()


@pytest.fixture()
def session():
    with requests.Session() as s:
        s.headers.update({"Accept": "application/json"})
        yield s
