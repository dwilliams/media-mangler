#!/usr/bin/env python3

### IMPORTS ###
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

from mmangler.models import FileModel

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class File(SQLAlchemyObjectType):
    class Meta:
        model = FileModel
        interfaces = (relay.Node, )

class FileConnection(relay.Connection):
    class Meta:
        node = File
