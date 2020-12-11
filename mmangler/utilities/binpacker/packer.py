#!/usr/bin/env python3

### IMPORTS ###
import logging

from operator import attrgetter

from .exceptions import ItemLargerThanBinSizeException
from .bin import BinPackerBin
from .item import BinPackerItem

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class BinPacker:
    def __init__(self, bin_size):
        self.logger = logging.getLogger(type(self).__name__)
        self.bin_size = int(bin_size)
        # Set? to hold items in queue
        self.item_queue = set()
        # Set? to hold bins
        self.bins = set()

    def __str__(self):
        return "BinPacker QueueLength: {}".format(len(self.item_queue))

    # Method (property?) to return list of bins?

    # Method (property?) to return list of lists of items in bins?

    # Method to add item to queue
    def add_item(self, item_key, item_size):
        if int(item_size) > self.bin_size:
            raise ItemLargerThanBinSizeException()
        self.item_queue.add(BinPackerItem(item_key, int(item_size)))

    # Method to perform the bin packing with a very naive algorithm
    def pack_naive(self):
        # Sort the queue by item size descending
        items = sorted(self.item_queue, key = attrgetter('item_size'), reverse = True)
        # For each item, check each available bin if there's enough space
        # if enough space, add to bin
        # otherwise create a new bin and add the item
        for item in items:
            placed = False
            for bin in self.bins:
                if item.item_size < bin.bin_free:
                    bin.add_item(item)
                    placed = True
            if not placed:
                new_bin = BinPackerBin(self.bin_size)
                new_bin.add_item(item)
                self.bins.add(new_bin)

    # In the future: Can add more method with better algorithms here.
