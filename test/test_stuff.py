
from fastapi.testclient import TestClient

import beetlapi

from beetlapi import app


testclient = TestClient(app)

def test_testclient_present():
    assert testclient
