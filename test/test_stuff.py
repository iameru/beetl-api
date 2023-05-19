from fastapi.testclient import TestClient
from beetlapi import app
from test import factory
import unittest
import random

testclient = TestClient(app)

testdata = {}

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

    testdata['open'] = beetl

def test_post_valid_closed_beetl():

    closed_beetl  = factory.beetl(beetlmode='closed')

    response = testclient.post(url='/beetl', json=closed_beetl)
    assert response.status_code == 200
    beetl = response.json()
    assert beetl.get('beetlmode') == 'closed'

    testdata['closed'] = beetl

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

def test_get_bids_does_return_empty_list_of_bids_and_total_when_empty():

    beetl = factory.beetl()
    testclient.post(url='/beetl', json=beetl)
    
    data = {'slug': beetl.get('slug'), 'obfuscation': beetl.get('obfuscation')}
    response = testclient.get('/bids',params=data)

    r = response.json()
    assert r.get('bids') == []
    assert r.get('bids_total') == 0

def test_get_bids_empty_for_secret_beetl():

    beetl = factory.beetl(beetlmode='closed')
    testclient.post(url='/beetl', json=beetl)
    
    data = {'slug': beetl.get('slug'), 'obfuscation': beetl.get('obfuscation')}
    response = testclient.get('/bids',params=data)

    r = response.json()
    assert r.get('bids') == []
    assert r.get('bids_total') == 0

def test_create_bids_for_open_beetl():

    beetl = testdata['open']
    bids = factory.create_bids(
        beetl_obfuscation= beetl.get('obfuscation'),
        beetl_slug= beetl.get('slug'), 
        amount=1
    )
    bid = bids[0]

    response = testclient.post('/bid', json=bid)
    assert response.status_code == 200
    b = response.json()
    assert b.get('secretkey')
    assert b.get('updated')

    testdata['open_bids'] = [b]

    bids = factory.create_bids(
        beetl_obfuscation= beetl.get('obfuscation'),
        beetl_slug= beetl.get('slug'), 
        amount=4
    )
    for bid in bids:
        response = testclient.post('/bid', json=bid)
        testdata['open_bids'].append(response.json())

    assert len(testdata['open_bids']) == 5

def test_get_bids_for_open_beetl():

    beetl = testdata['open']

    data = {
        'slug': beetl.get('slug'), 
        'obfuscation': beetl.get('obfuscation')
    }
    response = testclient.get('/bids',params=data)
    r_bids = response.json()

    assert r_bids.get('bids_total') == 5
    assert len(r_bids.get('bids')) == 5


    # gotta remove keys as they shall not be in the open poll
    bids = []
    for _bid in testdata.get('open_bids'):
        bid = _bid.copy()
        del bid['secretkey']
        bids.append(bid)

    _bids = r_bids.get('bids')

    # hackaround because I can compare lists of dicts easily with unittest
    case = unittest.TestCase()
    case.assertCountEqual(bids, _bids)

def test_edit_existing_bid_with_none_or_wrong_key():

    beetl = testdata.get('open')
    bid = random.choice(testdata.get('open_bids'))
    updated = bid.get('updated')

    bid = bid.copy()
    bid.update({'name' : 'francis mc. edit'})

    del bid['secretkey']
    response = testclient.patch('/bid', json=bid)
    assert response.status_code == 422

    bid['secretkey'] = 'l33th4xx'
    response = testclient.patch('/bid', json=bid)
    assert response.status_code == 422

    # fetching block repeating myself but i dont care for now
    data = {
        'slug': beetl.get('slug'), 
        'obfuscation': beetl.get('obfuscation')
    }
    response = testclient.get('/bids',params=data)

    bids = []
    for _bid in testdata.get('open_bids'):
        bid = _bid.copy()
        del bid['secretkey']
        bids.append(bid)
    r_bids = response.json()
    _bids = r_bids.get('bids')

    # hackaround because I can compare lists of dicts easily with unittest
    case = unittest.TestCase()
    case.assertCountEqual(bids, _bids)

def test_edit_existing_bid_with_correct_key():

    beetl = testdata.get('open')
    bid_selector = 2
    bid = testdata.get('open_bids')[bid_selector]

    max = bid.get('max')
    created = bid.get('created')
    updated = bid.get('updated')

    new_bid = bid.copy()
    new_bid.update({'name' : 'francis mc. edit', 'max': max+5})

    response = testclient.patch('/bid', json=new_bid)
    assert response.status_code == 200

    r_bid = response.json()
    
    assert r_bid.get('name') == 'francis mc. edit'
    assert r_bid.get('max') != max
    assert r_bid.get('max') == max + 5
    assert r_bid.get('created') == created
    assert r_bid.get('updated') != updated


