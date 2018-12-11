#!/usr/bin/env python3

### IMPORTS ###
import os
import responder

import mmangler.models
import mmangler.schemas

#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker

### GLOBALS ###
api = responder.API(title="Media Mangler", version="0.0.1", openapi="3.0.0", docs_route="/docs")
mmangler.schemas.attach_schemas(api)

### FUNCTIONS ###

### CLASSES ###

### MAIN ###
def main():
    #db_name = 'tmp_database.sqlite'

    api.run()

if __name__ == '__main__':
    main()
