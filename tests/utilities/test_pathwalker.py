#!/usr/bin/env python3

### IMPORTS ###
import logging
import os

from pyfakefs.fake_filesystem_unittest import TestCase

from mmangler.utilities.pathwalker import PathWalker

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class TestPathWalker(TestCase):
    def setUp(self):
        # Setup logging for the class
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("setUp")
        self.setUpPyfakefs()
        self.fs.create_dir('/walk')
        self.fs.create_dir('/walk/one')
        self.fs.create_dir('/walk/two')
        self.fs.create_file('/walk/filezero.txt')
        self.fs.create_file('/walk/one/one-zero.txt')
        self.fs.create_file('/walk/one/one-one.log')
        self.fs.create_file('/walk/one/one-two.bin')
        self.fs.create_file('/walk/two/two-zero.txt')
        self.fs.create_file('/walk/two/two-one.log')

    def test_walk_simple(self):
        self.logger.debug("test_walk_simple")
        # file_hash = FileHash(tmp_file_path)
        # self.assertEqual(file_hash.hash_sha512_hex, tmp_file_sha512)
        # self.assertEqual(file_hash.hash_md5_hex, tmp_file_md5)
        # self.assertEqual(str(file_hash), "FileHash File Path: {0}tmp{0}file.txt".format(os.sep))
        path_walker = PathWalker('/walk')
        self.assertEqual(len(path_walker.files_list), 6)
        self.assertEqual(len(path_walker.files_list_dicts), 6)