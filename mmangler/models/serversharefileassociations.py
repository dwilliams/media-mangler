#!/usr/bin/env python3

### IMPORTS ###
import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
#from sqlalchemy.sql import func

from .base import Base, GUID

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
'''
This is the instance of a unique file on a server share.
'''
class ServerShareFileAssociationModel(Base):
    __tablename__ = 'servershare_file_associations'
    id = Column(GUID(), primary_key = True, nullable = False, default = uuid.uuid4)
    servershares_id = Column(GUID(), ForeignKey('servershares.id'), nullable = False)
    files_id = Column(GUID(), ForeignKey('files.id'), nullable = False)
    file_path = Column(String(255), nullable = False)
    file_name = Column(String(255), nullable = False)
    last_seen = Column(DateTime, nullable = False, default = datetime.datetime.utcnow)
    servershare = relationship("ServerShareModel", back_populates = "files")
    file = relationship("FileModel", back_populates = "servershares")
