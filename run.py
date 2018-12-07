#!/usr/bin/env python3

### IMPORTS ###
import os

import mmangler.models

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###

### MAIN ###
def main():
    db_name = 'tmp_database.sqlite'
    if os.path.exists(db_name):
        os.remove(db_name)

    engine = create_engine('sqlite:///' + db_name)

    session = sessionmaker()
    session.configure(bind=engine)
    mmangler.models.Base.metadata.create_all(engine)

if __name__ == '__main__':
    main()
