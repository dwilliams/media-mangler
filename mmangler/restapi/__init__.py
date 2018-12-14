#!/usr/bin/env python3

### IMPORTS ###
from .files import FilesResource
from .medias import MediasResource, MediaIdResource

### GLOBALS ###

### FUNCTIONS ###
def attach_routes(api):
    api.add_route("/api/files/", FilesResource)
    api.add_route("/api/medias/", MediasResource)
    api.add_route("/api/medias/{media_id}/", MediaIdResource)

### CLASSES ###
