#!/usr/bin/env python3

### IMPORTS ###
from marshmallow import Schema, fields

from mmangler.models import FileTypeEnum

from .enum import EnumField

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class FileSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()
    size_bytes = fields.Integer()
    hash_sha512_hex = fields.String()  # Need to check the length
    file_type = EnumField(FileTypeEnum)
    date_added_to_collection = fields.DateTime()
    medias = fields.Nested('MediaSchema', many=True, exclude=('files',))
