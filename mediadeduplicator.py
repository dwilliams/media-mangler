#!/usr/bin/env python3

# This scanner will push directly to the database, not to the web server.

### IMPORTS ###
import argparse
#import enum
import hashlib
import logging
import os
#import psutil
#import win32api

import mmangler.models

#from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

### GLOBALS ###
#DB_URL = "mysql+pymysql://root:password@localhost:3306/mediamangler"

# Dictionary containing hashes
FILE_HASH_LISTS = {}
# {hash: [FileHash object, ...], ...}

### FUNCTIONS ###

### CLASSES ###
class FileHash:
    def __init__(self, file_path, file_name):
        self.logger = logging.getLogger(type(self).__name__)
        self.path = file_path
        self.name = file_name
        self.size_bytes = os.stat(self.path).st_size
        self._chunk_size = 65536
        self._hash_sha512 = hashlib.sha512()
        # ...
        self._hashfile()

    @property
    def hash_sha512_hex(self):
        return self._hash_sha512.hexdigest()

    def _hashfile(self):
        self.logger.debug("Path: %s", self.path)
        with open(os.path.join(self.path, self.name), 'rb') as tmp_file:
            while True:
                data = tmp_file.read(self._chunk_size)
                if not data:
                    break
                self._hash_sha512.update(data)
        logging.debug("SHA512: %s", self._hash_sha512.hexdigest())

    def get_path_name(self):
        return "FileHash: Path: \"{}\", Name: \"{}\"".format(self.path, self.name)

### MAIN ###
def main():
    parser = argparse.ArgumentParser(description="Scan and hash files on media, then push into the database.")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--dry", help="Dry run, don't push to database.", action="store_true")
    parser.add_argument("media_root", help="Path to the media root to be scanned.  Usually will be a drive letter (e.g. D:\).")
    args = parser.parse_args()

    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    logging.basicConfig(
        format=log_format,
        level=(logging.DEBUG if args.verbose else logging.INFO),
        filename='output-dedup.log'
    )

    logging.debug("Args: %s", args)
    #mmangler.models.prepare_db(DB_URL, echo=False)

    tmp_path = os.path.abspath(args.media_root)
    logging.info("Media Root: %s", tmp_path)

    _filename_ignore = [
        'WPSettings.dat',
        'IndexerVolumeGuid'
    ]

    tmp_filepath_list = []
    for dirpath, dirnames, filenames in os.walk(tmp_path):
        for filename in filenames:
            if filename not in _filename_ignore:
                #tmp_filepath_list.append(os.path.join(dirpath, filename))
                tmp_filepath_list.append({'dirpath': dirpath, 'filename': filename})

    tmp_file_counter = 0
    for item in tmp_filepath_list:
        tmp_file_counter = tmp_file_counter + 1
        logging.info("File Number: %d of %d", tmp_file_counter, len(tmp_filepath_list))
        logging.debug("    Name: %s / %s", item['dirpath'], item['filename'])

        # Hash the file
        tmp_file_hash = FileHash(item['dirpath'], item['filename'])

        # Add file to hash list, creating list if needed
        if not tmp_file_hash.hash_sha512_hex in FILE_HASH_LISTS:
            logging.debug("Creating a new list for new hash")
            FILE_HASH_LISTS[tmp_file_hash.hash_sha512_hex] = []
        logging.debug("Adding hash: %s", tmp_file_hash.hash_sha512_hex)
        FILE_HASH_LISTS[tmp_file_hash.hash_sha512_hex].append(tmp_file_hash)

    # Search through hash lists for lists with more than one hash
    LIST_FOR_SORTING = []
    for item in FILE_HASH_LISTS:
        if len(FILE_HASH_LISTS[item]) > 1:
            logging.info("Duplicate Hash: %s", item)
            logging.info("   Count: %d", len(FILE_HASH_LISTS[item]))
            for file_hash in FILE_HASH_LISTS[item]:
                logging.info(file_hash.get_path_name())
                LIST_FOR_SORTING.append(file_hash)

    # Sort by filename and Display the list
    logging.info("SORTED BY FILE NAME:")
    LIST_SORTED = sorted(LIST_FOR_SORTING, key = lambda i: i.name)
    for file_hash in LIST_SORTED:
        logging.info(file_hash.get_path_name())

if __name__ == '__main__':
    main()
