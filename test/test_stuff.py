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

def test_can_not_edit_beetl_without_key():

    slug = 'our-little-beetl'
    initial_title = 'initial title'
    beetl = factory.beetl(slug='our-little-beetl', title=initial_title, beetlmode='public')
    obfuscation = beetl.get('obfuscation')

    # make alteration
    updated = beetl.copy()
    updated.update({'title': 'updated title', 'description': 'updated description'})

    # post and extract secretkey
    response = testclient.post(url='/beetl', json=beetl)
    secretkey = response.json().get('secretkey')

    # update via patch
    response = testclient.patch('/beetl', json=updated)

    assert response.status_code == 422

def test_can_not_edit_beetl_with_fake_secretkey():

    slug = 'our-little-beetl'
    initial_title = 'initial title'
    beetl = factory.beetl(slug='our-little-beetl', title=initial_title)
    obfuscation = beetl.get('obfuscation')

    # make alteration
    updated = beetl.copy()
    updated.update({'title': 'updated title', 'description': 'updated description'})

    # post and extract secretkey
    response = testclient.post(url='/beetl', json=beetl)
    secretkey = response.json().get('secretkey')

    # update via patch and use secretkey
    updated.update({'secretkey': 'FAKE'})
    response = testclient.patch('/beetl', json=updated)

    assert response.status_code == 422

def test_can_edit_beetl_with_correct_key():

    slug = 'our-little-beetl'
    initial_title = 'initial title'
    beetl = factory.beetl(slug='our-little-beetl', title=initial_title)
    obfuscation = beetl.get('obfuscation')

    # make alteration
    updated = beetl.copy()
    updated.update({'title': 'updated title', 'description': 'updated description'})

    # post and extract secretkey
    response = testclient.post(url='/beetl', json=beetl)
    secretkey = response.json().get('secretkey')

    # update via patch and use secretkey
    updated.update({'secretkey': secretkey})
    response = testclient.patch('/beetl', json=updated)

    assert response.status_code == 200

    r = response.json()
    assert r.get('title') != initial_title
    assert r.get('title') == 'updated title'
    assert r.get('description') == 'updated description'

def test_get_beetl_doesnt_return_secrets():

    beetl = factory.beetl()
    testclient.post(url='/beetl', json=beetl)
    
    data = {'slug': beetl.get('slug'), 'obfuscation': beetl.get('obfuscation')}
    response = testclient.get('/beetl',params=data)

    assert response.status_code == 200
    
    r = response.json()
    assert r.get('amount') == beetl.get('amount')
    assert not r.get('secretkey')
