from fastapi.testclient import TestClient
from beetlapi import app
from test import factory

testclient = TestClient(app)

def test_testclient_present():
    assert testclient

def test_post_invalid_open_beetl():

    beetl = {
        'method': 'test without OBF and without SLUG',
        'beetlmode': 'SHALL FAIL',
    }
    response = testclient.post(url='/beetl', json=beetl)
    assert response.status_code == 422


def test_post_valid_open_beetl():

    open_beetl = factory.beetl(beetlmode='open')

    response = testclient.post(url='/beetl', json=open_beetl)
    assert response.status_code == 200
    beetl = response.json()
    assert beetl.get('beetlmode') == 'open'
    assert beetl.get('target') != 0

def test_post_valid_closed_beetl():

    closed_beetl  = factory.beetl(beetlmode='closed')

    response = testclient.post(url='/beetl', json=closed_beetl)
    assert response.status_code == 200
    assert response.json().get('beetlmode') == 'closed'


def test_post_throws_back_secret_key_to_edit_beetl():

    post_beetl = factory.beetl()
    response = testclient.post(url='/beetl', json=post_beetl)
    beetl = response.json()
    assert beetl.get('secretkey')