#!/usr/bin/env python3

### IMPORTS ###
import pytest

import mmangler

### GLOBALS ###

### FUNCTIONS ###
@pytest.fixture
def api():
    tmp_api = mmangler.prepare_api(db_url='sqlite:///test.sqlite?check_same_thread=False', echo=False)
    mmangler.models.Base.metadata.create_all(mmangler.models._engine)

    with mmangler.models._engine.connect() as conn:
        conn.execute('DELETE FROM media_file_associations;')
        conn.execute('DELETE FROM medias;')
        conn.execute('DELETE FROM files;')


    # Add media for use with file relations
    tmp_new_media = mmangler.models.MediaModel(
        name = "Test Media One",
        media_type = "HDD",
        capacity_bytes = 1234567890
    )
    tmp_session = mmangler.models.db_session()
    tmp_session.add(tmp_new_media)
    tmp_session.commit()

    return tmp_api

def test_files_get_no_data(api):
    # Case Specific Setup

    # Put test values here
    test_body = '[]' # JSON empty list

    r = api.requests.get(url="/api/files/")
    assert r.status_code == 200
    assert r.text == test_body

def test_files_get_one_entry(api):
    # Case Specific Setup
    tmp_new_file = mmangler.models.FileModel(
        name = "Test File One.dat",
        file_type = "other",
        size_bytes = 1234,
        hash_sha512_hex = "ABCD"
    )
    tmp_session = mmangler.models.db_session()
    tmp_session.add(tmp_new_file)
    tmp_session.commit()

    # Put test values here
    test_body = '[{"id": 1, "name": "Test File One.dat", "file_type": "other"}]'

    r = api.requests.get(url="/api/files/")
    assert r.status_code == 200
    assert r.text == test_body

def test_files_get_one_entry_by_id(api):
    # Case Specific Setup
    tmp_new_file = mmangler.models.FileModel(
        name = "Test File One.dat",
        file_type = "other",
        size_bytes = 1234,
        hash_sha512_hex = "ABCD"
    )
    tmp_session = mmangler.models.db_session()
    tmp_session.add(tmp_new_file)
    tmp_session.commit()

    # Put test values here
    #test_body = ''

    r = api.requests.get(url="/api/files/1/")
    assert r.status_code == 200
    #assert r.text == test_body

def test_medias_post_one_entry(api):
    # Case Specific Setup

    # Put test values here
    test_body = '[{"id": 1, "name": "Test File One.dat", "file_type": "other"}]'
    test_dict = {
        "name": "Test File One.dat",
        "file_type": "other",
        "size_bytes": 1234,
        "hash_sha512_hex": "ABCD",
        "media_id": 1
    }

    r1 = api.requests.post(url="/api/files/", json=test_dict)
    assert r1.status_code == 201

    r2 = api.requests.get(url="/api/files/")
    assert r2.status_code == 200
    assert r2.text == test_body

### CLASSES ###
