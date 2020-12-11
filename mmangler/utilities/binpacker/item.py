#!/usr/bin/env python3

### IMPORTS ###
import logging

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class BinPackerItem:
    def __init__(self, item_key, item_size):
        self.logger = logging.getLogger(type(self).__name__)
        self.item_key = item_key
        self.item_size = int(item_size)

    def __str__(self):
        return "BinPackerItem Key: {}, Size: {}".format(self.item_key, self.item_size)
