#!/usr/bin/env python3

### IMPORTS ###
import enum

from sqlalchemy import Column, Enum, Integer, String
#from sqlalchemy.ext.declarative import declarative_base

from .base import Base

### GLOBALS ###
#Base = declarative_base()

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
    media_type = Column(Enum(MediaTypeEnum), nullable=False) # 'HDD', 'CD', 'DVD', 'BR', 'CLOUD', 'TAPE'
    capacity_mb = Column(Integer, nullable=False)
    desc_location = Column(String)
    desc_make_model = Column(String)
