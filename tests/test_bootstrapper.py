import pytest
from flask import json
import time

from bootstrapper import bootstrapper


@pytest.fixture
def client():
    client = bootstrapper.app.test_client()
    yield client


def test_index(client):
    """
    Hello world test!
    :param client: test client
    :return: test assertions
    """
    print("Test: Basic Availability".center(79, '-'))

    rv = client.get('/')
    assert b'Bootstrapper' in rv.data


def test_caching(client):
    """
    Tests tests the caching system get and set objects
    :param client: test client
    :return: test assertions
    """
    print("Test: Caching".center(79, '-'))

    params = {
        'contents': 'CACHE TEST'
    }
    r = client.post('/set', data=json.dumps(params), content_type='application/json')
    d = json.loads(r.data)
    assert d['success'] is True
    assert d['key'] is not None

    key = d['key']
    r = client.get('/get/%s' % key)
    d = r.data
    assert b'CACHE TEST' in d


def test_build_openstack_archive(client):
    """
    Tests build openstack_configs
    :param client: test client
    :return: test assertions
    """
    print("Test: Build Openstack Archive".center(79, '-'))

    params = {
        "deployment_type": "openstack",
        "hostname": "panos-81",
        "auth_key": "v123",
        "archive_type": "zip",
        "management_ip": "192.168.1.100",
        "management_netmask": "255.255.255.0",
        "management_gateway": "192.168.1.254",
        "dns_server": "192.168.1.2",
        "outside_ip": "192.168.2.100",
        "inside_ip": "192.168.3.100",
        "ethernet2_1_profile": "PINGSSHTTPS",
        "ethernet1_1_profile": "PINGSSHTTPS",
        "default_next_hop": "10.10.10.10"
    }
    r = client.post('/generate_bootstrap_package', data=json.dumps(params), content_type='application/json')
    assert r.status_code == 200


def test_get_bootstrap_variables(client):
    """
    Tests the api to retrieve the list of variables in the bootstrap.xml template
    :param client: test client
    :return: test assertions
    """
    print("Test: Get Template Variables".center(79, '-'))

    params = {
        "bootstrap_template": "Default bootstrap.xml"
    }
    r = client.post('/get_bootstrap_variables', data=json.dumps(params), content_type='application/json')
    assert r.status_code == 200
    d = json.loads(r.data)
    assert d['success'] is True
    assert d['payload'] is not None


def test_import_template(client):
    """
    Tests the api to import template files
    :param client: test client
    :return: test assertions
    """
    print("Test: Import Template".center(79, '-'))

    params = {
        "name": "TEST_IMPORT",
        "description": "ADDED BY PYTEST",
        "template": "ASDFDFLKSDF:LKSD:KLSDF:LKSFDLDS:LKSDF:LKSD:LKSD:FLKSDF:KLSD:F"
    }
    r = client.post('/import_template', data=json.dumps(params), content_type='application/json')
    assert r.status_code == 200
    d = json.loads(r.data)
    assert d['success'] is True


def test_get_template(client):
    """
    Tests the api to retrieve template files
    :param client: test client
    :return: test assertions
    """
    print("Test: Get Template".center(79, '-'))
    params = {
        "template_name": "TEST_IMPORT"
    }
    r = client.post('/get_template', data=json.dumps(params), content_type='application/json')
    print(r)
    assert r.status_code == 200
    assert b"ASDF" in r.data


def test_list_templates(client):
    """
    Tests the api to retrieve the list of templates. This will test listed all files that are present in the
    configuration as well as any files that are present in the import directory. Manually create a file on the
    filesystem and verify it shows up in the list. This allows the operator to import files on startup via
    docker volumes or ansible or whatever
    :param client: test client
    :return: test assertions
    """

    print("Test: List Templates".center(79, '-'))
    r = client.get('/list_templates')
    assert r.status_code == 200
    d = json.loads(r.data)
    assert d['success'] is True
    assert d['templates'] is not None

    # mow iter over all found templates and verify we have all we need here (imported and manually created)
    found_import = False
    for t in d['templates']:
        if t['name'] == 'TEST_IMPORT':
            found_import = True

    print(d)
    assert found_import is True


def test_delete_template(client):
    """
    Tests the api to delete template files
    :param client: test client
    :return: test assertions
    """

    print("Test: Delete Template".center(79, '-'))
    params = {
        "template_name": "TEST_IMPORT"
    }
    r = client.post('/delete_template', data=json.dumps(params), content_type='application/json')
    assert r.status_code == 200
    d = json.loads(r.data)
    assert d['success'] is True

    # also delete our manually created file as well
    params = {
        "template_name": "MANUAL_IMPORT"
    }
    m = client.post('/delete_template', data=json.dumps(params), content_type='application/json')
    assert m.status_code == 200

