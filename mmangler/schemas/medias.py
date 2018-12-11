#!/usr/bin/env python3

### IMPORTS ###
from marshmallow import Schema, fields

from mmangler.models import MediaTypeEnum

from .enum import EnumField

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class MediaSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()
    media_type = EnumField(MediaTypeEnum)
    capacity_bytes = fields.Integer()
    date_added_to_collection = fields.DateTime()
    desc_location = fields.String()
    desc_make_model = fields.String()
    files = fields.Nested('FileSchema', many=True, exclude=('medias',))
