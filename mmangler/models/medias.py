#!/usr/bin/env python3

### IMPORTS ###
import enum

from sqlalchemy import BigInteger, Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base

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
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    media_type = Column(
        Enum(*[name for name, member in MediaTypeEnum.__members__.items()], name="mediatypeenum"),
        nullable=False
    )
    capacity_bytes = Column(BigInteger, nullable=False)
    date_added_to_collection = Column(DateTime, server_default=func.now(), nullable=False)
    desc_location = Column(String)
    desc_make_model = Column(String)
    files = relationship("MediaFileAssociationModel", back_populates="media")
