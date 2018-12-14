#!/usr/bin/env python3

### IMPORTS ###
from .files import FileSchema  # noqa: F401
from .medias import MediaSchema  # noqa: F401
from .mediafileassociations import MediaFileAssociationSchema  # noqa: F401

### GLOBALS ###

### FUNCTIONS ###
def attach_schemas(api):
    api.add_schema("File", FileSchema)
    api.add_schema("Media", MediaSchema)

### CLASSES ###
