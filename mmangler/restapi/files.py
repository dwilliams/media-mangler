#!/usr/bin/env python3

### IMPORTS ###
import mmangler.models
import mmangler.schemas

import json

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class FilesResource:
    def on_get(self, request, response):
        tmp_file_schema = mmangler.schemas.FileSchema(many=True)
        tmp_results = mmangler.models.FileModel.query.all()
        response.text = json.dumps(tmp_file_schema.dump(tmp_results))

class FileIdResource:
    def on_get(self, request, response, *, file_id):
        tmp_file_schema = mmangler.schemas.FileSchema()
        tmp_result = mmangler.models.FileModel.query.get(file_id)
        response.text = json.dumps(tmp_file_schema.dump(tmp_result))
