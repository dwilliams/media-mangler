#!/usr/bin/env python3

### IMPORTS ###
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

from mmangler.models import MediaModel

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class Media(SQLAlchemyObjectType):
    class Meta:
        model = MediaModel
        interfaces = (relay.Node, )

class MediaConnection(relay.Connection):
    class Meta:
        node = Media
