#!/usr/bin/env python3

### IMPORTS ###
import hashlib
import logging
import os

from pathlib import Path

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class NotAFileException(Exception):
    pass

class FileHash:
    def __init__(self, file_path, chunk_size = 65536):
        self.logger = logging.getLogger(type(self).__name__)
        self.file_path = Path(file_path)
        if not self.file_path.is_file():
            raise NotAFileException
        self.chunk_size = chunk_size
        self.size_bytes = os.stat(self.file_path).st_size
        self._hash_sha512 = hashlib.sha512()
        self._hash_md5 = hashlib.md5()
        self._hash_file()

    def __str__(self):
        return "FileHash File Path: {}".format(self.file_path)

    @property
    def hash_sha512_hex(self):
        return self._hash_sha512.hexdigest()

    @property
    def hash_md5_hex(self):
        return self._hash_md5.hexdigest()

    def _hash_file(self):
        self.logger.debug("Path: %s", self.file_path)
        with open(self.file_path, 'rb') as tmp_file:
            while True:
                data = tmp_file.read(self.chunk_size)
                if not data:
                    break
                self._hash_sha512.update(data)
                self._hash_md5.update(data)
        logging.debug("SHA512: 0x%s", self._hash_sha512.hexdigest())
        logging.debug("   MD5: 0x%s", self._hash_md5.hexdigest())