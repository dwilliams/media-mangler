#!/usr/bin/env python3

### IMPORTS ###
import hashlib
import logging
import os

from pathlib import Path

from mmangler.exceptions import NotAFileException

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class FileHash:
    def __init__(self, file_path, chunk_size = 65536):
        self.logger = logging.getLogger(type(self).__name__)
        self.path = Path(file_path)
        if not self.path.is_file():
            raise NotAFileException
        self.chunk_size = chunk_size
        self.size_bytes = os.stat(self.path).st_size
        self._hash_sha512 = hashlib.sha512()
        self._hash_md5 = hashlib.md5()
        self._hash_file()

    def __str__(self):
        return "FileHash File Path: {}".format(self.path)

    @property
    def hash_sha512_hex(self):
        return self._hash_sha512.hexdigest()

    @property
    def hash_md5_hex(self):
        return self._hash_md5.hexdigest()

    def _hash_file(self):
        self.logger.debug("Path: %s", self.path)
        with open(self.path, 'rb') as tmp_file:
            while True:
                data = tmp_file.read(self.chunk_size)
                if not data:
                    break
                self._hash_sha512.update(data)
                self._hash_md5.update(data)
        self.logger.debug("SHA512: 0x%s", self._hash_sha512.hexdigest())
        self.logger.debug("MD5: 0x%s", self._hash_md5.hexdigest())