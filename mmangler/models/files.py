#!/usr/bin/env python3

### IMPORTS ###
#import enum

from sqlalchemy import BigInteger, Column, Enum, Integer, String

from .base import Base

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
#class MediaTypeEnum(enum.Enum):
#    HDD = 1
#    CD = 2
#    DVD = 3
#    BR = 4
#    CLOUD = 5
#    TAPE = 6

class FileModel(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    hash_sha512_hex = Column(String(128), nullable=False)

# FIXME:
# Note to self:
#    Next step is to add a many to many relationship between files and medias.
#    Following step is to setup alembic or flyway for versioned DB creation.
#    After, copy the responder, graphene, etc from the example script to this project.