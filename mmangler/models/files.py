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
class FileTypeEnum(enum.Enum):
    other = 1
    video = 2
    audio = 3
    photo = 4
    text = 5

class FileModel(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    hash_sha512_hex = Column(String(128), nullable=False)
    file_type = Column(Enum(FileTypeEnum), nullable=False)
    date_added_to_collection = Column(DateTime, server_default=func.now(), nullable=False)
    medias = relationship("MediaFileAssociationModel", back_populates="file")
