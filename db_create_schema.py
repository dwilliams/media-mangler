#!/usr/bin/env python3

# This scanner will push directly to the database, not to the web server.

### IMPORTS ###
import mmangler.models

### GLOBALS ###
DB_URL = "mysql+pymysql://root:password@localhost:3306/mediamangler"

### FUNCTIONS ###

### CLASSES ###

### MAIN ###
def main():
    mmangler.models.prepare_db(DB_URL, echo=True)

    try:
        mmangler.models.Base.metadata.create_all(mmangler.models._engine)
    except Exception as ex:
        # Something else is wrong, so bail out
        print("Exception: {}".format(ex))
    #finally:
    #    pass

if __name__ == '__main__':
    main()
