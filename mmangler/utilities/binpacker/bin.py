#!/usr/bin/env python3

### IMPORTS ###
import logging

from .exceptions import NotBinPackerItemException, NotEnoughSpaceInBinException
from .item import BinPackerItem

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class BinPackerBin:
    def __init__(self, bin_size):
        self.logger = logging.getLogger(type(self).__name__)
        self.bin_size = int(bin_size)
        self.bin_items = set()

    def __str__(self):
        return "BinPackerBin Size: {}".format(self.bin_size)

    # Method (property) to get free space in bin
    @property
    def bin_free(self):
        tmp_free = self.bin_size
        for item in self.bin_items:
            tmp_free = tmp_free - item.item_size
        return tmp_free

    # Method (property) to return list of items in bin

    # Method to add item
    def add_item(self, item):
        if not isinstance(item, BinPackerItem):
            raise NotBinPackerItemException(str(item))
        if item.item_size > self.bin_free:
            raise NotEnoughSpaceInBinException(str(self), str(item))
        self.bin_items.add(item)
