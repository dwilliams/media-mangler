#!/usr/bin/env python3

### IMPORTS ###
import datetime
import enum
import uuid

from sqlalchemy import BigInteger, Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship
#from sqlalchemy.sql import func

from .base import Base, GUID

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
'''
This is a unique file that can be copied to a media.
'''
class FileTypeEnum(enum.Enum):
    other = 'other'
    video = 'video'
    audio = 'audio'
    photo = 'photo'
    text = 'text'

class FileModel(Base):
    __tablename__ = 'files'
    id = Column(GUID(), primary_key = True, nullable = False, default = uuid.uuid4)
    metadata_name = Column(String(255), nullable = False)
    size_bytes = Column(BigInteger, nullable = False)
    hash_sha512_hex = Column(String(128), nullable = False)
    hash_md5_hex = Column(String(32), nullable = False)
    file_type = Column(
        Enum(*[name for name, member in FileTypeEnum.__members__.items()], name = "filetypeenum"),
        nullable = False
    )
    date_added_to_collection = Column(DateTime, nullable = False, default = datetime.datetime.utcnow)
    medias = relationship("MediaFileAssociationModel", back_populates = "file")
