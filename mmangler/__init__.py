#!/usr/bin/env python3

### IMPORTS ###
import logging

import responder

import mmangler.exceptions

import mmangler.models
import mmangler.schemas
import mmangler.graph
import mmangler.restapi

### GLOBALS ###

### FUNCTIONS ###
def prepare_api(db_url='sqlite:///database.sqlite', echo=False):
    mmangler.models.prepare_db(db_url, echo=echo)
    tmp_cors_params = {'allow_origins': ['*']}
    api = responder.API(
        title="Media Mangler",
        version="0.0.1",
        openapi="3.0.0",
        docs_route="/docs",
        cors=True,
        cors_params=tmp_cors_params
    )
    mmangler.schemas.attach_schemas(api)
    mmangler.graph.attach_routes(api)
    mmangler.restapi.attach_routes(api)
    return api

### CLASSES ###
