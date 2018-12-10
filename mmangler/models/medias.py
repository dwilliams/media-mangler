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
    HDD = 1
    CD = 2
    DVD = 3
    BR = 4
    CLOUD = 5
    TAPE = 6

class MediaModel(Base):
    __tablename__ = 'medias'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    media_type = Column(Enum(MediaTypeEnum), nullable=False)
    capacity_bytes = Column(BigInteger, nullable=False)
    date_added_to_collection = Column(DateTime, server_default=func.now(), nullable=False)
    desc_location = Column(String)
    desc_make_model = Column(String)
    files = relationship("MediaFileAssociationModel", back_populates="media")
