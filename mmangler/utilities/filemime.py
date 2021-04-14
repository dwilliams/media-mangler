#!/usr/bin/env python3

### IMPORTS ###
import logging

from pathlib import Path

from winmagic import magic

from mmangler.exceptions import NotAFileException
from mmangler.models import FileTypeEnum

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class FileMime:
    _mime_overrides = {
        "text/x-python": FileTypeEnum.other
    }

    def __init__(self, file_path):
        self.logger = logging.getLogger(type(self).__name__)
        self.path = Path(file_path)
        if not self.path.is_file():
            raise NotAFileException
        self.type = FileTypeEnum.other
        self._magic_mimer = magic.Magic(mime = True)
        self._mime_file()

    def __str__(self):
        return "FileMime File Path: {}, Type: {}".format(self.path)

    def _mime_file(self):
        self.logger.debug("Path: %s", self.path)
        tmp_mimetype = self._magic_mimer.from_file(str(self.path))
        self.logger.debug("Mime Type: %s", tmp_mimetype)
        if tmp_mimetype in self._mime_overrides.keys():
            self.type = self._mime_overrides[tmp_mimetype]
        elif tmp_mimetype.startswith("video"):
            self.type = FileTypeEnum.video
        elif tmp_mimetype.startswith("audio"):
            self.type = FileTypeEnum.audio
        elif tmp_mimetype.startswith("image"):
            self.type = FileTypeEnum.photo
        elif tmp_mimetype.startswith("text"):
            self.type = FileTypeEnum.text
        self.logger.debug("File Type: %s", self.type)
