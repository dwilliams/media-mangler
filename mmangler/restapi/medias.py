#!/usr/bin/env python3

### IMPORTS ###
import json

import mmangler.models
import mmangler.schemas

#from sqlalchemy.orm import noload

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class MediasResource:
    def on_get(self, request, response):
        tmp_media_schema = mmangler.schemas.MediaSchema(many=True)
        tmp_results = mmangler.models.MediaModel.query.all()
        response.text = json.dumps(tmp_media_schema.dump(tmp_results).data)

class MediaIdResource:
    def on_get(self, request, response, *, media_id):
        tmp_media_schema = mmangler.schemas.MediaSchema()
        tmp_result = mmangler.models.MediaModel.query.get(media_id)
        response.text = json.dumps(tmp_media_schema.dump(tmp_result).data)
