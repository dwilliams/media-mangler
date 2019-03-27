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
        conn.execute('DELETE FROM medias;')
    return tmp_api

def test_medias_get_no_data(api):
    # Case Specific Setup

    # Put test values here
    test_body = '[]' # JSON empty list

    r = api.requests.get(url="/api/medias/")
    assert r.status_code == 200
    assert r.text == test_body

def test_medias_get_one_entry(api):
    # Case Specific Setup
    tmp_new_media = mmangler.models.MediaModel(
        name = "Test Media One",
        media_type = "HDD",
        capacity_bytes = 1234567890
    )
    tmp_session = mmangler.models.db_session()
    tmp_session.add(tmp_new_media)
    tmp_session.commit()

    # Put test values here
    test_body = '[{"id": 1, "name": "Test Media One", "media_type": "HDD"}]'

    r = api.requests.get(url="/api/medias/")
    assert r.status_code == 200
    assert r.text == test_body

def test_medias_get_one_entry_by_id(api):
    # Case Specific Setup
    tmp_new_media = mmangler.models.MediaModel(
        name = "Test Media One",
        media_type = "HDD",
        capacity_bytes = 1234567890,
        desc_make_model = "Test Make Test Model",
        desc_location = "Someplace Else"
    )
    tmp_session = mmangler.models.db_session()
    tmp_session.add(tmp_new_media)
    tmp_session.commit()

    # Put test values here
    #test_body = ''

    r = api.requests.get(url="/api/medias/1/")
    assert r.status_code == 200
    #assert r.text == test_body

def test_medias_post_one_entry(api):
    # Case Specific Setup

    # Put test values here
    test_body = '[{"id": 1, "name": "Test Media One", "media_type": "HDD"}]'
    test_dict = {
        "name": "Test Media One",
        "media_type": "HDD",
        "capacity_bytes": 1234567890
    }

    r1 = api.requests.post(url="/api/medias/", json=test_dict)
    assert r1.status_code == 201

    r2 = api.requests.get(url="/api/medias/")
    assert r2.status_code == 200
    assert r2.text == test_body

### CLASSES ###
