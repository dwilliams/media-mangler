#!/usr/bin/env python3

### IMPORTS ###
# import os
import logging

import responder

import mmangler.models
import mmangler.schemas
import mmangler.graph
import mmangler.restapi

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

### GLOBALS ###
db_url = 'sqlite:///tmp_database.sqlite'

#engine = create_engine(db_url)
#Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#db_session = scoped_session(Session)
#
#mmangler.models.Base.query = db_session.query_property()

mmangler.models.prepare_db(db_url)

api = responder.API(title="Media Mangler", version="0.0.1", openapi="3.0.0", docs_route="/docs")
mmangler.schemas.attach_schemas(api)
mmangler.graph.attach_routes(api)
mmangler.restapi.attach_routes(api)

### FUNCTIONS ###

### CLASSES ###

### MAIN ###
def main():
    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    logging.basicConfig(
        format=log_format,
        level=logging.DEBUG
    )

    api.run()

if __name__ == '__main__':
    main()
