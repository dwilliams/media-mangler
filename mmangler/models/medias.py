#!/usr/bin/env python3

### IMPORTS ###
from sqlalchemy import Column, Enum, Integer, String
#from sqlalchemy.ext.declarative import declarative_base

from .base import Base

### GLOBALS ###
#Base = declarative_base()

### FUNCTIONS ###

### CLASSES ###
class MediaModel(Base):
    __tablename__ = 'medias'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    media_type = Column(Enum('HDD', 'CD', 'DVD', 'BR', 'CLOUD', 'TAPE'), nullable=False)
    capacity_mb = Column(Integer, nullable=False)
    desc_location = Column(String)
    desc_make_model = Column(String)
