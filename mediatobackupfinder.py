#!/usr/bin/env python3

# This scans a folder in the file server and checks to see if any of the files are lacking backups.
# (e.g. less than 2 backups)

### IMPORTS ###
import argparse
import hashlib
import logging
import os

import mmangler.models

from mmangler.exceptions import ConflictException, MultipleResultsException, ServerErrorException

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

### GLOBALS ###
DB_URL = "mysql+pymysql://root:password@localhost:3306/mediamangler"

### FUNCTIONS ###

### CLASSES ###
class FileInfo:
    def __init__(self, file_path):
        self.logger = logging.getLogger(type(self).__name__)
        self.path = file_path
        self.name = os.path.splitext(os.path.basename(self.path))[0]
        self.size_bytes = os.stat(self.path).st_size
        self._chunk_size = 65536
        self._hash_sha512 = hashlib.sha512()
        self._hash_md5 = hashlib.md5()
        # ...
        self._hashfile()

    @property
    def hash_sha512_hex(self):
        return self._hash_sha512.hexdigest()

    @property
    def hash_md5_hex(self):
        return self._hash_md5.hexdigest()

    def _hashfile(self):
        self.logger.debug("Path: %s", self.path)
        with open(self.path, 'rb') as tmp_file:
            while True:
                data = tmp_file.read(self._chunk_size)
                if not data:
                    break
                self._hash_sha512.update(data)
                self._hash_md5.update(data)
        logging.debug("SHA512: %s", self._hash_sha512.hexdigest())
        logging.debug("MD5: %s", self._hash_md5.hexdigest())

class FileChecker:
    def __init__(self, file_path, backup_count = 1):
        self.logger = logging.getLogger(type(self).__name__)
        self.path = file_path
        self.backup_count = backup_count
        # ...
        self.file_info = FileInfo(self.path)
        self._checkfile()

    def _checkfile(self):
        tmp_session = mmangler.models.db_session()
        try:
            # Check to see if file exists in files table
            tmp_db_file_result = tmp_session.query(mmangler.models.FileModel).filter_by(hash_sha512_hex = self.file_info.hash_sha512_hex).one()
            self.logger.debug("File Result: %s", tmp_db_file_result.__dict__)
            if tmp_db_file_result.hash_md5_hex == self.file_info.hash_md5_hex and tmp_db_file_result.size_bytes == self.file_info.size_bytes:
                # if file entry:
                #    count the number of entries for file in associations table
                #    # https://stackoverflow.com/questions/14754994/why-is-sqlalchemy-count-much-slower-than-the-raw-query
                tmp_mfa_list = tmp_session.query(mmangler.models.MediaFileAssociationModel).filter_by(files_id = tmp_db_file_result.id).all()
                self.logger.debug("MFA List: (%d) %s", len(tmp_mfa_list), tmp_mfa_list)
                #    if less than backup number argument, log "<file> has # backups on <types>"
                #    if greater than or equal to backup number argument, do nothing
                if len(tmp_mfa_list) < self.backup_count:
                    self.logger.info("File %s has %d backups:", self.path, len(tmp_mfa_list))
                    for item in tmp_mfa_list:
                        self.logger.info("  Type: %-4s   Name: %s", item.media.media_type, item.media.name)
            else:
                self.logger.warning("HASH COLLISION\n  Path: %s\n  Hash (SHA512): %s", self.path, self.file_info.hash_sha512_hex)
        except NoResultFound:
            # if no file entry, log "<file> has 0 backups"
            self.logger.info("File %s has 0 backups", self.path)
        finally:
            tmp_session.close()

### MAIN ###
def main():
    parser = argparse.ArgumentParser(description = "Scan a folder and check if backups exist in the database.")
    parser.add_argument("-v", "--verbose", action = "store_true")
    parser.add_argument("--backup_count", type = int, help = "The number of backups expected.")
    parser.add_argument("media_dir", help = "Path to the directory containing media to be scanned.")
    args = parser.parse_args()

    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    logging.basicConfig(
        format=log_format,
        level=(logging.DEBUG if args.verbose else logging.INFO)
    )

    logging.debug("Args: %s", args)
    mmangler.models.prepare_db(DB_URL, echo=False)

    tmp_path = os.path.abspath(args.media_dir)
    logging.info("Media Directory: %s", tmp_path)

    _filename_ignore = [
        'WPSettings.dat',
        'IndexerVolumeGuid'
    ]

    tmp_filepath_list = []
    for dirpath, dirnames, filenames in os.walk(tmp_path):
        for filename in filenames:
            if filename not in _filename_ignore:
                tmp_filepath_list.append(os.path.join(dirpath, filename))

    tmp_file_counter = 0
    for item in tmp_filepath_list:
        tmp_file_counter = tmp_file_counter + 1
        logging.info("File Number: %d of %d", tmp_file_counter, len(tmp_filepath_list))
        FileChecker(file_path = item, backup_count = args.backup_count)

if __name__ == '__main__':
    main()
