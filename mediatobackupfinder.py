#!/usr/bin/env python3

# This scans a folder in the file server and checks to see if any of the files are lacking backups.
# (e.g. less than 2 backups)

### IMPORTS ###
import argparse
import logging
import os

import mmangler.models

from pathlib import Path

from mmangler.utilities.pathwalker import PathWalker
from mmangler.utilities.filehash import FileHash
from mmangler.utilities.binpacker import BinPacker

from mmangler.exceptions import ConflictException, MultipleResultsException, ServerErrorException

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class FileInfo:
    def __init__(self, file_path):
        self.logger = logging.getLogger(type(self).__name__)
        self.path = Path(file_path)
        self.name = os.path.splitext(os.path.basename(self.path))[0]
        self.size_bytes = os.stat(self.path).st_size
        self._filehash = FileHash(self.path)

class FileChecker:
    #def __init__(self, file_path, backup_count = 1):
    def __init__(self, file_path):
        self.logger = logging.getLogger(type(self).__name__)
        self.path = Path(file_path)
        #self.backup_count = backup_count
        self.current_backup_count = 0
        self.has_backup_br = False
        self.has_backup_hdd = False
        # ...
        self.file_info = FileInfo(self.path)
        self._checkfile()

    def _checkfile(self):
        tmp_session = mmangler.models.db_session()
        try:
            # Check to see if file exists in files table
            tmp_db_file_result = tmp_session.query(mmangler.models.FileModel).filter_by(hash_sha512_hex = self.file_info._filehash.hash_sha512_hex).one()
            self.logger.debug("File Result: %s", tmp_db_file_result.__dict__)
            if tmp_db_file_result.hash_md5_hex == self.file_info._filehash.hash_md5_hex and tmp_db_file_result.size_bytes == self.file_info.size_bytes:
                # if file entry:
                #    count the number of entries for file in associations table
                #    # https://stackoverflow.com/questions/14754994/why-is-sqlalchemy-count-much-slower-than-the-raw-query
                tmp_mfa_list = tmp_session.query(mmangler.models.MediaFileAssociationModel).filter_by(files_id = tmp_db_file_result.id).all()
                self.logger.debug("MFA List: (%d) %s", len(tmp_mfa_list), tmp_mfa_list)
                #    if less than backup number argument, log "<file> has # backups on <types>"
                #    if greater than or equal to backup number argument, do nothing
                self.current_backup_count = len(tmp_mfa_list)
                # if self.current_backup_count < self.backup_count:
                #     self.logger.info("File %s has %d backups:", self.path, self.current_backup_count)
                #     for item in tmp_mfa_list:
                #         self.logger.info("  Type: %-4s   Name: %s", item.media.media_type, item.media.name)
                for item in tmp_mfa_list:
                    self.logger.debug("  Type: %-4s   Name: %s", item.media.media_type, item.media.name)
                    if item.media.media_type == mmangler.models.MediaTypeEnum.BR:
                        self.has_backup_br = True
                    elif item.media.media_type == mmangler.models.MediaTypeEnum.HDD:
                        self.has_backup_hdd = True
            else:
                self.logger.warning("HASH COLLISION\n  Path: %s\n  Hash (SHA512): %s", self.path, self.file_info._filehash.hash_sha512_hex)
        except NoResultFound:
            # if no file entry, log "<file> has 0 backups"
            self.logger.info("File %s has 0 backups", self.path)
        finally:
            tmp_session.close()

### MAIN ###
def main():
    parser = argparse.ArgumentParser(description = "Scan a folder and check if backups exist in the database.")
    parser.add_argument("-v", "--verbose", action = "store_true")
    parser.add_argument("--db_user", default = "root", help = "Set the database username.")
    parser.add_argument("--db_pass", default = "password", help = "Set the database password.")
    parser.add_argument("--db_host", default = "localhost", help = "Set the database hostname.")
    parser.add_argument("--db_port", default = "3306", help = "Set the database network port.")
    parser.add_argument("--db_name", default = "mediamangler", help = "Set the database name.")
    #parser.add_argument("--backup_count", type = int, default = 1, help = "The number of backups expected.")
    parser.add_argument("--exclude_dirs", help = "Comma separated string of directories to exclude from scan.")
    parser.add_argument("--size_br_images", type = int, default = 0, help = "Size of Blu-ray images to pack (in GB).")
    parser.add_argument("media_dir", help = "Path to the directory containing media to be scanned.")
    args = parser.parse_args()

    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    logging.basicConfig(
        format=log_format,
        level=(logging.DEBUG if args.verbose else logging.INFO)
    )

    logging.debug("Args: %s", args)
    mmangler.models.prepare_db("mysql+pymysql://{}:{}@{}:{}/{}".format(
        args.db_user, args.db_pass, args.db_host, args.db_port, args.db_name
    ), echo = False)

    tmp_path = os.path.abspath(args.media_dir)
    logging.info("Media Directory: %s", tmp_path)

    path_walker = PathWalker(tmp_path, args.exclude_dirs.split(',') if args.exclude_dirs else [])

    to_pack_br = {}

    # Check to see if the file has backups and track which files don't have a BR backup
    tmp_file_counter = 0
    for item in path_walker.files_list:
        tmp_file_counter = tmp_file_counter + 1
        logging.info("File Number: %d of %d", tmp_file_counter, len(path_walker.files_list))
        #FileChecker(file_path = item, backup_count = args.backup_count)
        tmp_filechecker = FileChecker(item)
        if not tmp_filechecker.has_backup_br:
            to_pack_br[item] = tmp_filechecker.file_info.size_bytes


    if args.size_br_images > 0:
        # Pack the files into bins
        tmp_packer = BinPacker(args.size_br_images * 1000 * 1000 * 1000) # Using 1000 instead of 1024 for each size conversion
        for item in to_pack_br:
            tmp_packer.add_item(item, to_pack_br[item])
        tmp_packer.pack_naive()

        # Print the bins
        for tmp_bin in tmp_packer.bins:
            logging.info("Bin ------------ %s ( %d free )", str(tmp_bin), tmp_bin.bin_free)
            for item in tmp_bin.bin_items:
                logging.info("  %s", str(item))

if __name__ == '__main__':
    main()
