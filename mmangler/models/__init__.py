#!/usr/bin/env python3

### IMPORTS ###
from .base import Base  # noqa: F401
from .files import FileModel, FileTypeEnum  # noqa: F401
from .medias import MediaModel, MediaTypeEnum  # noqa: F401
from .mediafileassociations import MediaFileAssociationModel  # noqa: F401

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

### GLOBALS ###
_engine = None
_session_factory = None
db_session = None

### FUNCTIONS ###
def prepare_db(url, echo=False):
    global _engine
    global _session_factory
    global db_session
    _engine = create_engine(url, echo=echo)
    _session_factory = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    db_session = scoped_session(_session_factory)

    Base.query = db_session.query_property()

### CLASSES ###
