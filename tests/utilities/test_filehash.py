#!/usr/bin/env python3

### IMPORTS ###
import logging
import os
#import unittest

#import unittest.mock as mock
from pyfakefs.fake_filesystem_unittest import TestCase

from mmangler.utilities.filehash import FileHash, NotAFileException

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class TestFileHash(TestCase):
    def setUp(self):
        # Setup logging for the class
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("setUp")
        self.setUpPyfakefs()

    def test_hash_file(self):
        self.logger.debug("test_hash_file")
        tmp_file_path = '/tmp/file.txt'
        tmp_file_contents = 'thisisatest'
        tmp_file_sha512 = 'd44edf261feb71975ee9275259b2eab75920d312cb1481a024306002dc57bf680e0c3b5a00edb6ffd15969369d8a714ccce1396937a57fd057ab312cb6c6d8b6'
        tmp_file_md5 = 'f830f69d23b8224b512a0dc2f5aec974'
        self.fs.create_file(tmp_file_path, contents = tmp_file_contents)
        file_hash = FileHash(tmp_file_path)
        self.assertEqual(file_hash.hash_sha512_hex, tmp_file_sha512)
        self.assertEqual(file_hash.hash_md5_hex, tmp_file_md5)
        self.assertEqual(str(file_hash), "FileHash File Path: {0}tmp{0}file.txt".format(os.sep))

    def test_hash_directory(self):
        self.logger.debug("test_hash_directory")
        tmp_dir_path = '/tmp/'
        self.fs.create_dir(tmp_dir_path)
        with self.assertRaises(NotAFileException):
            file_hash = FileHash(tmp_dir_path)
