#!/usr/bin/env python3

### IMPORTS ###
import graphene
import responder

from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField

from mmangler.models import FileModel, MediaModel

from .files import FileConnection
from .medias import MediaConnection

### GLOBALS ###

### FUNCTIONS ###
def attach_routes(api):
    schema = graphene.Schema(query=Query)
    #schema.execute(context_value={'session': session})
    view = responder.ext.GraphQLView(api=api, schema=schema)
    api.add_route("/graph", view)

### CLASSES ###
class Query(graphene.ObjectType):
    node = relay.Node.Field()
    all_medias = SQLAlchemyConnectionField(MediaConnection)
    all_files = SQLAlchemyConnectionField(FileConnection)

    # def resolve_all_medias(self, info, **kwargs):
    #     return MediaModel.query.all()
