#!/usr/bin/env python3

### IMPORTS ###
from marshmallow import Schema, fields

from mmangler.models import MediaTypeEnum

from .enum import EnumField

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class MediaFileAssociationSchema(Schema):
    id = fields.Integer(dump_only=True)
    media = fields.Nested('MediaSchema', many=False, exclude=('files', ))
    file = fields.Nested('FileSchema', many=False, exclude=('medias', ))
