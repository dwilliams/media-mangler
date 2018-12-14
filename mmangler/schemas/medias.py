#!/usr/bin/env python3

### IMPORTS ###
from marshmallow import Schema, fields, post_dump, pre_dump

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
    files = fields.Nested('MediaFileAssociationSchema', many=True, dump_only=True, exclude=('media','medias'))

    @post_dump(pass_many=True)
    def simplify_list(self, data, many):
        tmp_data = []
        if many:
            for item in data:
                tmp_data.append({
                    'id': item['id'],
                    'name': item['name'],
                    'media_type': item['media_type']
                })
        else:
            tmp_data = data
        return tmp_data

    @pre_dump(pass_many=True)
    def simplist(self, data, many):
        print("MediaSchema simplist data: {}".format(data))
        return data

# FIXME:
# NOTE:
# - Trying to use the same schema for the lists, which could have large sublists, doesn't seem to be working.
#   Likely need to use two separate schemas.
