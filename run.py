#!/usr/bin/env python3

### IMPORTS ###
import logging

import mmangler

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###

### MAIN ###
def main():
    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    logging.basicConfig(
        format=log_format,
        level=logging.DEBUG
    )

    api = mmangler.prepare_api(db_url='sqlite:///tmp_database.sqlite')

    api.run()

if __name__ == '__main__':
    main()
