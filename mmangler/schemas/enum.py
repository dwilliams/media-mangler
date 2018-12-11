#!/usr/bin/env python3

### IMPORTS ###
from marshmallow import fields, validate

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class EnumField(fields.Field):
    """Validates against a given set of enumerated values."""
    def __init__(self, enum, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum = enum
        self.validators.insert(0, validate.OneOf([v.value for v in self.enum]))

    def _serialize(self, value, attr, obj):
        return self.enum(value).value

    def _deserialize(self, value):
        return self.enum(value)

    def _validate(self, value):
        if type(value) is self.enum:
            super()._validate(value.value)
        else:
            super()._validate(value)
