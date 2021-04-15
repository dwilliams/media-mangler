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
class ServerShareModel(Base):
    __tablename__ = 'servershares'
    id = Column(GUID(), primary_key = True, nullable = False, default = uuid.uuid4)
    name = Column(String(255), nullable = False)
    desc_location = Column(String(255))
    desc_make_model = Column(String(255))
    files = relationship("ServerShareFileAssociationModel", back_populates = "servershare")
