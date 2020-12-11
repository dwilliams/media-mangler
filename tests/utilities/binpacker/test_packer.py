#!/usr/bin/env python3

### IMPORTS ###
import logging
import unittest
import uuid

from mmangler.utilities.binpacker import BinPacker
from mmangler.utilities.binpacker import NotBinPackerItemException, NotEnoughSpaceInBinException, ItemLargerThanBinSizeException

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class TestBinPackerCreation(unittest.TestCase):
    def setUp(self):
        # Setup logging for the class
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("setUp")

    def test_create(self):
        self.logger.debug("test_create")
        test_bin_size = 2345
        packer = BinPacker(test_bin_size)
        self.logger.debug("Created Packer: %s", packer)
        self.assertIsInstance(packer, BinPacker)
        self.assertEqual(packer.bin_size, test_bin_size)
        self.assertEqual(len(packer.item_queue), 0)
        self.assertEqual(len(packer.bins), 0)

    def test_create_size_string(self):
        self.logger.debug("test_create")
        test_bin_size = '2345'
        packer = BinPacker(test_bin_size)
        self.logger.debug("Created Packer: %s", packer)
        self.assertIsInstance(packer, BinPacker)
        self.assertEqual(packer.bin_size, int(test_bin_size))
        self.assertEqual(len(packer.item_queue), 0)
        self.assertEqual(len(packer.bins), 0)

class TestBinPackerItems(unittest.TestCase):
    def setUp(self):
        # Setup logging for the class
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("setUp")
        # Packer for testing
        self.bin_size = 2345
        self.packer = BinPacker(self.bin_size)

    def test_add_item(self):
        self.logger.debug("test_add_item")
        self.assertEqual(len(self.packer.bins), 0)
        self.assertEqual(len(self.packer.item_queue), 0)
        self.assertEqual(self.packer.bin_size, self.bin_size)
        test_item_key = uuid.uuid4().hex
        test_item_size = 1234
        self.packer.add_item(test_item_key, test_item_size)
        self.assertEqual(len(self.packer.bins), 0)
        self.assertEqual(len(self.packer.item_queue), 1)

    def test_add_item_too_big(self):
        self.logger.debug("test_add_item_too_big")
        self.assertEqual(len(self.packer.bins), 0)
        self.assertEqual(len(self.packer.item_queue), 0)
        self.assertEqual(self.packer.bin_size, self.bin_size)
        test_item_key = uuid.uuid4().hex
        test_item_size = 12340
        with self.assertRaises(ItemLargerThanBinSizeException):
            self.packer.add_item(test_item_key, test_item_size)

class TestBinPackerNaivePacker(unittest.TestCase):
    def setUp(self):
        # Setup logging for the class
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("setUp")
        # Packer for testing
        self.bin_size = 2345
        self.packer = BinPacker(self.bin_size)

    def test_pack_one_item(self):
        self.logger.debug("test_pack_one_item")
        self.assertEqual(len(self.packer.bins), 0)
        test_item_key = uuid.uuid4().hex
        test_item_size = 1234
        self.packer.add_item(test_item_key, test_item_size)
        self.packer.pack_naive()
        self.assertEqual(len(self.packer.bins), 1) # One bin
        self.assertEqual(len(list(self.packer.bins)[0].bin_items), 1) # One item in the one bin
        self.assertEqual(list(list(self.packer.bins)[0].bin_items)[0].item_key, test_item_key)
        self.assertEqual(list(list(self.packer.bins)[0].bin_items)[0].item_size, test_item_size)

    def test_pack_three_items(self):
        self.logger.debug("test_pack_one_item")
        self.assertEqual(len(self.packer.bins), 0)
        test_item_keys = [uuid.uuid4().hex, uuid.uuid4().hex, uuid.uuid4().hex]
        test_item_sizes = [1234, 123, 2344]
        for i in range(len(test_item_keys)):
            self.packer.add_item(test_item_keys[i], test_item_sizes[i])
        self.packer.pack_naive()
        self.assertEqual(len(self.packer.bins), 2) # Two bins
        # FIXME: Figure out how to check the two bins for the correct items.  Look up in list maybe?

    def test_pack_seven_items(self):
        self.logger.debug("test_pack_one_item")
        self.assertEqual(len(self.packer.bins), 0)
        # seven items calc'd to fit in four bins: 3, 2, 1, 1
        test_item_keys = [uuid.uuid4().hex, uuid.uuid4().hex, uuid.uuid4().hex, uuid.uuid4().hex, uuid.uuid4().hex, uuid.uuid4().hex, uuid.uuid4().hex]
        test_item_sizes = [1234, 123, 2344, 2100, 1050, 142, 975]
        for i in range(len(test_item_keys)):
            self.packer.add_item(test_item_keys[i], test_item_sizes[i])
        self.packer.pack_naive()
        self.assertEqual(len(self.packer.bins), 4) # Two bins
        # FIXME: Figure out how to check the four bins for the correct items.  Look up in list maybe?
