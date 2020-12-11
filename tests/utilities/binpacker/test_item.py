#!/usr/bin/env python3

### IMPORTS ###
import logging
import unittest
import uuid

from mmangler.utilities.binpacker import BinPackerItem

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class TestBinPackerItemCreation(unittest.TestCase):
    def setUp(self):
        # Setup logging for the class
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("setUp")

    def test_create(self):
        self.logger.debug("test_create")
        test_item_key = uuid.uuid4().hex
        test_item_size = 1234
        item = BinPackerItem(test_item_key, test_item_size)
        self.logger.debug("Created Item: %s", item)
        self.assertIsInstance(item, BinPackerItem)
        self.assertEqual(item.item_key, test_item_key)
        self.assertEqual(item.item_size, test_item_size)

    def test_create_size_string(self):
        self.logger.debug("test_create_size_string")
        test_item_key = uuid.uuid4().hex
        test_item_size = '4567'
        item = BinPackerItem(test_item_key, test_item_size)
        self.logger.debug("Created Item: %s", item)
        self.assertIsInstance(item, BinPackerItem)
        self.assertEqual(item.item_key, test_item_key)
        self.assertEqual(item.item_size, int(test_item_size))
