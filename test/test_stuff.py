from fastapi.testclient import TestClient
from beetlapi import app
from test import factory
import unittest
import random
from beetlapi.database.main import engine, Bid, Beetl
from sqlmodel import Session, select

testclient = TestClient(app)

# In here there is testdata for public beetl:
# 'open'
# 'open_bids'
# private:
# 'closed' 
# 'closed_bids'
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

    open_beetl = factory.beetl(beetlmode='public')

    response = testclient.post(url='/beetl', json=open_beetl)
    assert response.status_code == 200
    beetl = response.json()
    assert beetl.get('beetlmode') == 'public'
    assert beetl.get('target') != 0

    testdata['open'] = beetl

def test_post_valid_closed_beetl():

    closed_beetl  = factory.beetl(beetlmode='private')

    response = testclient.post(url='/beetl', json=closed_beetl)
    assert response.status_code == 200
    beetl = response.json()
    assert beetl.get('beetlmode') == 'private'

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

    assert response.status_code == 404

    data = {'slug': beetl.get('slug'), 'obfuscation': beetl.get('obfuscation')}
    response = testclient.get('/beetl',params=data)
    assert response.json().get('title') != updated.get('title')
    assert response.json().get('description') == beetl.get('description')

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

    beetl = factory.beetl(beetlmode='private')
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
    assert response.status_code == 404

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

def test_create_bids_for_closed_beetl():

    beetl = testdata['closed']
    bids = factory.create_bids(
        beetl_obfuscation= beetl.get('obfuscation'),
        beetl_slug= beetl.get('slug'), 
        amount=1
    )
    bid = bids[0]

    response = testclient.post('/bid', json=bid)
    b = response.json()

    testdata['closed_bids'] = [b]

    bids = factory.create_bids(
        beetl_obfuscation= beetl.get('obfuscation'),
        beetl_slug= beetl.get('slug'), 
        amount=4
    )
    for bid in bids:
        response = testclient.post('/bid', json=bid)
        testdata['closed_bids'].append(response.json())

    assert len(testdata['closed_bids']) == 5

def test_get_bids_for_closed_beetl():

    beetl = testdata['closed']

    data = {
        'slug': beetl.get('slug'), 
        'obfuscation': beetl.get('obfuscation')
    }
    response = testclient.get('/bids',params=data)
    r_bids = response.json()

    assert r_bids.get('bids_total') == 5
    assert len(r_bids.get('bids')) == 0

def test_delete_bid_wrong_nonexistent_key():

    bid = random.choice(testdata.get('open_bids'))

    params = {
        'beetl_obfuscation': bid.get('beetl_obfuscation'),
        'beetl_slug': bid.get('beetl_slug'),
              }

    response = testclient.delete('/bid', params=params)
    assert response.status_code == 422

    params['secretkey'] = 'dis shall fail aswell'

    response = testclient.delete('/bid', params=params)
    assert response.status_code == 404

def test_delete_bid():

    bid = testdata.get('open_bids')[2]

    with Session(engine) as session:
        db_bid = session.exec(
            select(Bid)
            .where(Bid.beetl_obfuscation == bid.get('beetl_obfuscation'))
            .where(Bid.beetl_slug ==        bid.get('beetl_slug'))
            .where(Bid.secretkey ==         bid.get('secretkey'))
        ).first()

    assert db_bid

    params = {
        'beetl_obfuscation': bid.get('beetl_obfuscation'),
        'beetl_slug': bid.get('beetl_slug'),
        'secretkey': bid.get('secretkey'),
              }

    response = testclient.delete('/bid', params=params)
    assert response.status_code == 200



    with Session(engine) as session:
        db_bid = session.exec(
            select(Bid)
            .where(Bid.beetl_obfuscation == bid.get('beetl_obfuscation'))
            .where(Bid.beetl_slug ==        bid.get('beetl_slug'))
            .where(Bid.secretkey ==         bid.get('secretkey'))
        ).first()

    assert not db_bid

    del testdata.get('open_bids')[2]

def test_delete_beetl_wrong_nonexistent_key():

    beetl = testdata.get('open')

    params = {
        'obfuscation': beetl.get('obfuscation'),
        'slug': beetl.get('slug'),
              }

    response = testclient.delete('/beetl', params=params)
    assert response.status_code == 422

    params['secretkey'] = 'dis shall fail aswell'

    response = testclient.delete('/beetl', params=params)
    assert response.status_code == 404

def test_delete_beetl():

    beetl = testdata.get('open')

    with Session(engine) as session:
        db_beetl = session.exec(
            select(Beetl)
            .where(Beetl.obfuscation == beetl.get('obfuscation'))
            .where(Beetl.slug == beetl.get('slug'))
        ).first()

    assert db_beetl

    params = {
        'obfuscation': beetl.get('obfuscation'),
        'slug': beetl.get('slug'),
        'secretkey': beetl.get('secretkey'),
              }

    response = testclient.delete('/beetl', params=params)
    assert response.status_code == 200

    with Session(engine) as session:
        db_beetl = session.exec(
            select(Beetl)
            .where(Beetl.obfuscation == beetl.get('obfuscation'))
            .where(Beetl.slug == beetl.get('slug'))
        ).first()

    assert not db_beetl

def test_delete_beetl_deletes_all_its_bids_aswell():

    bid = testdata.get('closed_bids')[1]

    with Session(engine) as session:
        db_bid = session.exec(
            select(Bid)
            .where(Bid.beetl_obfuscation == bid.get('beetl_obfuscation'))
            .where(Bid.beetl_slug ==        bid.get('beetl_slug'))
        ).first()

    assert db_bid


    beetl = testdata.get('closed')
    params = {
        'obfuscation': beetl.get('obfuscation'),
        'slug': beetl.get('slug'),
        'secretkey': beetl.get('secretkey'),
              }
    response = testclient.delete('/beetl', params=params)
    assert response.status_code == 200

    with Session(engine) as session:
        db_bid = session.exec(
            select(Bid)
            .where(Bid.beetl_obfuscation == bid.get('beetl_obfuscation'))
            .where(Bid.beetl_slug ==        bid.get('beetl_slug'))
        ).all()

    assert not db_bid

