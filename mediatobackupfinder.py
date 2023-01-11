#!/usr/bin/env python3

# This scans a folder in the file server and checks to see if any of the files are lacking backups.
# (e.g. less than 2 backups)

### IMPORTS ###
import argparse
import logging
#import os
import sys

import mmangler.models

from pathlib import Path

#from mmangler.utilities.pathwalker import PathWalker
#from mmangler.utilities.filehash import FileHash
from mmangler.utilities.binpacker import BinPacker

#from mmangler.exceptions import ConflictException, MultipleResultsException, ServerErrorException

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

### GLOBALS ###

### FUNCTIONS ###
def get_share_by_name(db_session, share_name):
    logging.debug("Searching for share with name: %s", share_name)
    # Figure out which share we're wanting to work with
    #tmp_session = mmangler.models.db_session()
    tmp_db_share_result = None
    try:
        tmp_db_share_result = db_session.query(mmangler.models.ServerShareModel).filter_by(name = share_name).one()
        logging.debug("Share Result: %s", tmp_db_share_result.__dict__)
    except NoResultFound:
        # if no share entry:
        logging.error("Share doesn't exist: %s", share_name)
    # finally:
    #     tmp_session.close()
    return tmp_db_share_result

def get_files_by_share(db_session, share_obj):
    logging.debug("Gathering file list for share: %s", share_obj.name)
    #tmp_session = mmangler.models.db_session()
    tmp_db_files_list = None
    try:
        tmp_db_files_list = db_session.query(mmangler.models.ServerShareFileAssociationModel).filter_by(
            servershares_id = share_obj.id
        ).all()
    except NoResultFound:
        # if no files in share:
        logging.error("No files in share: %s", share_obj.name)
    return tmp_db_files_list

### CLASSES ###
# class FileInfo:
#     def __init__(self, file_path):
#         self.logger = logging.getLogger(type(self).__name__)
#         self.path = Path(file_path)
#         self.name = os.path.splitext(os.path.basename(self.path))[0]
#         self.size_bytes = os.stat(self.path).st_size
#         self._filehash = FileHash(self.path)

# class FileChecker:
#     #def __init__(self, file_path, backup_count = 1):
#     def __init__(self, file_path):
#         self.logger = logging.getLogger(type(self).__name__)
#         self.path = Path(file_path)
#         #self.backup_count = backup_count
#         self.current_backup_count = 0
#         self.has_backup_br = False
#         self.has_backup_hdd = False
#         # ...
#         self.file_info = FileInfo(self.path)
#         self._checkfile()
#
#     def _checkfile(self):
#         tmp_session = mmangler.models.db_session()
#         try:
#             # Check to see if file exists in files table
#             tmp_db_file_result = tmp_session.query(mmangler.models.FileModel).filter_by(hash_sha512_hex = self.file_info._filehash.hash_sha512_hex).one()
#             self.logger.debug("File Result: %s", tmp_db_file_result.__dict__)
#             if tmp_db_file_result.hash_md5_hex == self.file_info._filehash.hash_md5_hex and tmp_db_file_result.size_bytes == self.file_info.size_bytes:
#                 # if file entry:
#                 #    count the number of entries for file in associations table
#                 #    # https://stackoverflow.com/questions/14754994/why-is-sqlalchemy-count-much-slower-than-the-raw-query
#                 tmp_mfa_list = tmp_session.query(mmangler.models.MediaFileAssociationModel).filter_by(files_id = tmp_db_file_result.id).all()
#                 self.logger.debug("MFA List: (%d) %s", len(tmp_mfa_list), tmp_mfa_list)
#                 #    if less than backup number argument, log "<file> has # backups on <types>"
#                 #    if greater than or equal to backup number argument, do nothing
#                 self.current_backup_count = len(tmp_mfa_list)
#                 # if self.current_backup_count < self.backup_count:
#                 #     self.logger.info("File %s has %d backups:", self.path, self.current_backup_count)
#                 #     for item in tmp_mfa_list:
#                 #         self.logger.info("  Type: %-4s   Name: %s", item.media.media_type, item.media.name)
#                 for item in tmp_mfa_list:
#                     self.logger.debug("  Type: %-4s   Name: %s", item.media.media_type, item.media.name)
#                     if item.media.media_type == mmangler.models.MediaTypeEnum.BR:
#                         self.has_backup_br = True
#                     elif item.media.media_type == mmangler.models.MediaTypeEnum.HDD:
#                         self.has_backup_hdd = True
#             else:
#                 self.logger.warning("HASH COLLISION\n  Path: %s\n  Hash (SHA512): %s", self.path, self.file_info._filehash.hash_sha512_hex)
#         except NoResultFound:
#             # if no file entry, log "<file> has 0 backups"
#             self.logger.info("File %s has 0 backups", self.path)
#         finally:
#             tmp_session.close()

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
    parser.add_argument("--log_output_file", help = "File to output logging.")
    parser.add_argument("--manifest_output_file", help = "File to output binning result.")
    # FIXME: Should this be limited to 1 GB to 10000 GB (10 TB)?
    #        https://stackoverflow.com/questions/25295487/python-argparse-value-range-help-message-appearance
    parser.add_argument("--size_bins", type = int, default = 25, help = "Size of bins (e.g. Blu-ray images) to pack (in GB).")
    # FIXME: Should this be using the ID?
    parser.add_argument("share_name", help = "Name of the share that we want to check.")
    args = parser.parse_args()

    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    log_root = logging.getLogger()
    log_root.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    log_handler = None
    if args.log_output_file:
        log_handler = logging.FileHandler(args.log_output_file, 'w', 'utf-8')
    else:
        log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    log_handler.setFormatter(logging.Formatter(log_format))
    log_root.addHandler(log_handler)

    logging.debug("Args: %s", args)
    mmangler.models.prepare_db("mysql+pymysql://{}:{}@{}:{}/{}".format(
        args.db_user, args.db_pass, args.db_host, args.db_port, args.db_name
    ), echo = False)

    tmp_db_session = mmangler.models.db_session()

    # Figure out which share we're wanting to work with
    tmp_share = get_share_by_name(tmp_db_session, args.share_name)

    # Get the list of files on the share
    tmp_files_list = get_files_by_share(tmp_db_session, tmp_share)

    # Setup the bin packer
    tmp_packer = BinPacker(args.size_bins * 1000 * 1000 * 1000) # Using 1000 instead of 1024 for each size conversion

    # Check each file if it has a backup of type BR (if BR size is specified) or HDD
    for item_file in tmp_files_list:
        logging.debug("File data: %s", item_file.__dict__)

        # FIXME: Exclude subdirectories of shares here
        #        Hacking a quick ignore for paths starting with '[SORT]'
        if "[SORT]" in item_file.file_path:
            continue

        tmp_mfa_list = item_file.file.medias
        logging.debug("MFA List: (%d) %s", len(tmp_mfa_list), tmp_mfa_list)
        #    if less than backup number argument, log "<file> has # backups on <types>"
        #    if greater than or equal to backup number argument, do nothing
        #self.current_backup_count = len(tmp_mfa_list)
        # if self.current_backup_count < self.backup_count:
        #     self.logger.info("File %s has %d backups:", self.path, self.current_backup_count)
        #     for item in tmp_mfa_list:
        #         self.logger.info("  Type: %-4s   Name: %s", item.media.media_type, item.media.name)
        has_backup_br = False
        has_backup_hdd = False
        for item_mfa in tmp_mfa_list:
            logging.debug("  Type: %-4s   Name: %s", item_mfa.media.media_type, item_mfa.media.name)
            if item_mfa.media.media_type == mmangler.models.MediaTypeEnum.BR.value:
                has_backup_br = True
            elif item_mfa.media.media_type == mmangler.models.MediaTypeEnum.HDD.value:
                has_backup_hdd = True
        # If less or equal to than 100 GB, assume BR backup type, otherwise assume HDD type
        logging.debug("has_backup_br: %s, has_backup_hdd: %s", has_backup_br, has_backup_hdd)
        if (args.size_bins < 101 and not has_backup_br) or (args.size_bins > 100 and not has_backup_hdd):
            logging.debug("Adding item to packer")
            tmp_packer.add_item("{}/{}".format(item_file.file_path, item_file.file_name), item_file.file.size_bytes)

    # Pack the bins and print
    tmp_packer.pack_naive()
    if args.manifest_output_file:
        with open(Path(args.manifest_output_file), 'w', encoding = "utf-8") as filehandle:
            filehandle.write("Number of Bins: {:,}\n".format(len(tmp_packer.bins)))
            for tmp_bin in tmp_packer.bins:
                filehandle.write("\nBin ------------ Size: {:,} ( {:,} free )\n".format( tmp_bin.bin_size, tmp_bin.bin_free))
                for item in sorted(tmp_bin.bin_items, key = lambda x: x.item_key):
                    filehandle.write("   {} ( {:,} )\n".format(item.item_key, item.item_size))
    else:
        for tmp_bin in tmp_packer.bins:
            logging.info("Bin ------------ %s ( %d free )", str(tmp_bin), tmp_bin.bin_free)
            for item in tmp_bin.bin_items:
                logging.info("  %s", str(item))

    tmp_db_session.close()

if __name__ == '__main__':
    main()
