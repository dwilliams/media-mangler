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
class MediaTypeEnum(enum.Enum):
    HDD = 'HDD'
    CD = 'CD'
    DVD = 'DVD'
    BR = 'BR'
    CLOUD = 'CLOUD'
    TAPE = 'TAPE'

#MediaTypeEnumList = [name for name, member in MediaTypeEnum.__members__.items()]

class MediaModel(Base):
    __tablename__ = 'medias'
    id = Column(GUID(), primary_key = True, nullable = False, default = uuid.uuid4)
    name = Column(String(255), nullable = False)
    media_type = Column(
        Enum(*[name for name, member in MediaTypeEnum.__members__.items()], name = "mediatypeenum"),
        nullable = False
    )
    capacity_bytes = Column(BigInteger, nullable = False)
    date_added_to_collection = Column(DateTime, nullable = False, default = datetime.datetime.utcnow)
    desc_location = Column(String(255))
    desc_make_model = Column(String(255))
    files = relationship("MediaFileAssociationModel", back_populates = "media")
