#!/usr/bin/env python3

### IMPORTS ###
import logging
import psutil
import win32api

from pathlib import Path

from mmangler.models import MediaTypeEnum

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class MediaDiscover:
    def __init__(self, media_path):
        self.logger = logging.getLogger(type(self).__name__)
        self.path = Path(media_path)
        self.type = None
        self.name = None
        self.capacity_bytes = 0
        if self.path is not None:
            self._media_discover()

    def __str__(self):
        return "Media Discover Path: {}, Type: {}, Name: {}, Size: {}".format(self.path, self.type, self.name, self.capacity_bytes)

    def _media_discover(self):
        self.logger.debug("Discovering Media")
        # FIXME: Make this work for both winderps and loonix
        self.name = win32api.GetVolumeInformation(str(self.path))[0]
        self.logger.info("Media Label: %s", self.name)

        tmp_disk_usage = psutil.disk_usage(str(self.path))
        self.capacity_bytes = tmp_disk_usage.total
        self.logger.debug("Media Size: %d", tmp_disk_usage.total)

        tmp_disk_parts = psutil.disk_partitions()
        self.logger.debug("Checking partitions for path: %s", str(self.path))
        self.logger.debug("tmp_disk_parts: %s", tmp_disk_parts)
        for x in tmp_disk_parts:
            self.logger.debug("Path: %s (%s)", Path(x.device), x.device)
            self.logger.debug("Match: %s", Path(x.device).resolve() == self.path.resolve())
        tmp_disk_part = next(x for x in tmp_disk_parts if Path(x.device).resolve() == self.path.resolve())
        if tmp_disk_part.fstype in ["NTFS", "FAT", "FAT32"]:
            self.type = MediaTypeEnum.HDD
        elif (tmp_disk_part.fstype in ["CDFS"]) or ("cdrom" in tmp_disk_part.opts):
            if self.capacity_bytes < 737148928:  # 703 MiB (CD-R)
                self.type = MediaTypeEnum.CD
            elif self.capacity_bytes < 8547991552:  # 8.5 GiB (DVD-R DL)
                self.type = MediaTypeEnum.DVD
            else:
                self.type = MediaTypeEnum.BR
        self.logger.debug("Media Type: %s", self.type)
