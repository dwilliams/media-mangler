#!/usr/bin/env python3

### IMPORTS ###
from marshmallow import Schema, fields, post_dump

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
    medias = fields.Nested('MediaFileAssociationSchema', many=True, dump_only=True, exclude=('file','files'))

    @post_dump(pass_many=True)
    def simplify_list(self, data, many):
        print("FileSchema simplify_list data: {}".format(data))
        tmp_data = []
        if many:
            for item in data:
                tmp_data.append({
                    'id': item['id'],
                    'name': item['name'],
                    'file_type': item['file_type']
                })
        else:
            tmp_data = data
        return tmp_data
