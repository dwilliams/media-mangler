#!/usr/bin/env python3

### IMPORTS ###
from .files import FilesResource, FileIdResource
from .medias import MediasResource, MediaIdResource
from .root import RootResource

### GLOBALS ###

### FUNCTIONS ###
def attach_routes(api):
    api.add_route("/", RootResource)
    api.add_route("/api/files/", FilesResource)
    api.add_route("/api/files/{file_id}/", FileIdResource)
    api.add_route("/api/medias/", MediasResource)
    api.add_route("/api/medias/{media_id}/", MediaIdResource)

### CLASSES ###
