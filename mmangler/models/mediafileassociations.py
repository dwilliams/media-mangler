#!/usr/bin/env python3

### IMPORTS ###
import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class MediaFileAssociationModel(Base):
    __tablename__ = 'media_file_associations'
    medias_id = Column(Integer, ForeignKey('medias.id'), primary_key=True)
    files_id = Column(Integer, ForeignKey('files.id'), primary_key=True)
    date_copied_to_media = Column(DateTime, server_default=func.now(), nullable=False)
    media = relationship("MediaModel", back_populates="files")
    file = relationship("FilesModel", back_populates="medias")
