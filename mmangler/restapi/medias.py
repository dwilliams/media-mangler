#!/usr/bin/env python3

### IMPORTS ###
import mmangler.models
import mmangler.schemas

import json

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class MediasResource:
    def on_get(self, request, response):
        tmp_media_schema = mmangler.schemas.MediaSchema(many=True)
        tmp_results = mmangler.models.MediaModel.query.all()
        response.text = json.dumps(tmp_media_schema.dump(tmp_results))
