#!/usr/bin/env python3

### IMPORTS ###
import pytest

import mmangler

### GLOBALS ###

### FUNCTIONS ###
@pytest.fixture
def api():
    return mmangler.prepare_api(db_url='sqlite://', echo=True)

def test_root(api):
    test_body = "Root Page.  Put UI here."

    r = api.requests.get(url="/")
    assert r.status_code == 200
    assert r.text == test_body

### CLASSES ###
