#!/usr/bin/env python3

### IMPORTS ###
import logging
import unittest
import uuid

from mmangler.utilities.binpacker import BinPackerBin, BinPackerItem
from mmangler.utilities.binpacker import NotBinPackerItemException, NotEnoughSpaceInBinException

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class TestBinPackerBinCreation(unittest.TestCase):
    def setUp(self):
        # Setup logging for the class
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("setUp")

    def test_create(self):
        self.logger.debug("test_create")
        test_bin_size = 2345
        bin = BinPackerBin(test_bin_size)
        self.logger.debug("Created Bin: %s", bin)
        self.assertIsInstance(bin, BinPackerBin)
        self.assertEqual(bin.bin_size, test_bin_size)
        self.assertEqual(bin.bin_free, test_bin_size)
        self.assertEqual(len(bin.bin_items), 0)

    def test_create_size_string(self):
        self.logger.debug("test_create_size_string")
        test_bin_size = '2345'
        bin = BinPackerBin(test_bin_size)
        self.logger.debug("Created Bin: %s", bin)
        self.assertIsInstance(bin, BinPackerBin)
        self.assertEqual(bin.bin_size, int(test_bin_size))
        self.assertEqual(bin.bin_free, int(test_bin_size))
        self.assertEqual(len(bin.bin_items), 0)

class TestBinPackerBinItems(unittest.TestCase):
    def setUp(self):
        # Setup logging for the class
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("setUp")
        # Bin for testing
        self.bin_size = 2345
        self.test_bin = BinPackerBin(self.bin_size)
        # Items for testing
        #self.small_item = BinPackerItem(uuid.uuid4().hex, 1234)
        #self.big_item = BinPackerItem(uuid.uuid4().hex, 1234567890)

    def test_add_item(self):
        self.logger.debug("test_add_item")
        self.assertEqual(len(self.test_bin.bin_items), 0)
        self.assertEqual(self.test_bin.bin_size, self.bin_size)
        self.assertEqual(self.test_bin.bin_free, self.bin_size)
        test_item_size = 1234
        test_item = BinPackerItem(uuid.uuid4().hex, test_item_size)
        self.test_bin.add_item(test_item)
        self.assertEqual(len(self.test_bin.bin_items), 1)
        self.assertEqual(self.test_bin.bin_size, self.bin_size)
        self.assertEqual(self.test_bin.bin_free, self.bin_size - test_item_size)

    def test_add_item_too_big(self):
        self.logger.debug("test_add_item_too_big")
        self.assertEqual(len(self.test_bin.bin_items), 0)
        self.assertEqual(self.test_bin.bin_size, self.bin_size)
        self.assertEqual(self.test_bin.bin_free, self.bin_size)
        test_item_size = 12340
        test_item = BinPackerItem(uuid.uuid4().hex, test_item_size)
        with self.assertRaises(NotEnoughSpaceInBinException):
            self.test_bin.add_item(test_item)

    def test_add_non_item(self):
        with self.assertRaises(NotBinPackerItemException):
            self.test_bin.add_item('test_item')
