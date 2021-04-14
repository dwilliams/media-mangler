#!/usr/bin/env python3

# This scanner will push directly to the database, not to the web server.

### IMPORTS ###
import argparse
import logging
import os
import sys

from pathlib import Path

from mmangler.utilities.filehash import FileHash
from mmangler.utilities.pathwalker import PathWalker

### GLOBALS ###

# Dictionary containing hashes
FILE_HASH_LISTS = {}
# {hash: [FileHash object, ...], ...}

### FUNCTIONS ###

### CLASSES ###

### MAIN ###
def main():
    parser = argparse.ArgumentParser(description="Scan and hash files on media, then push into the database.")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--dry", help="Dry run, don't delete files.", action="store_true")
    parser.add_argument("--delete_from", help = "Directory from which duplicates will be deleted.")
    parser.add_argument("--exclude_dirs", help = "Comma separated string of directories to exclude from scan.")
    parser.add_argument("--output_file", help = "File to output logging.")
    parser.add_argument("media_root", help="Path to the media root to be scanned.  Usually will be a drive letter (e.g. D:\).")
    args = parser.parse_args()

    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    log_root = logging.getLogger()
    log_root.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    log_handler = None
    if args.output_file:
        log_handler = logging.FileHandler(args.output_file, 'w', 'utf-8')
    else:
        log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    log_handler.setFormatter(logging.Formatter(log_format))
    log_root.addHandler(log_handler)

    # if args.output_file:
    #     logging.basicConfig(
    #         format = log_format,
    #         level = (logging.DEBUG if args.verbose else logging.INFO),
    #         filename = args.output_file
    #     )
    # else:
    #     logging.basicConfig(
    #         format = log_format,
    #         level = (logging.DEBUG if args.verbose else logging.INFO)
    #     )
    logging.debug("Args: %s", args)

    logging.info("Media Root: %s", os.path.abspath(args.media_root))
    path_walker = PathWalker(os.path.abspath(args.media_root), args.exclude_dirs.split(',') if args.exclude_dirs else [])

    # Hash all of the files
    tmp_file_counter = 0
    tmp_file_list = path_walker.files_list
    for item in tmp_file_list:
        tmp_file_counter = tmp_file_counter + 1
        logging.info("File Number: %d of %d", tmp_file_counter, len(tmp_file_list))
        logging.debug("    Name: %s", item)
        try:
            # Hash the file
            tmp_file_hash = FileHash(item)
            # Add file to hash list, creating list if needed
            if not tmp_file_hash.hash_sha512_hex in FILE_HASH_LISTS:
                logging.debug("Creating a new list for new hash")
                FILE_HASH_LISTS[tmp_file_hash.hash_sha512_hex] = []
            logging.debug("Adding hash: %s", tmp_file_hash.hash_sha512_hex)
            FILE_HASH_LISTS[tmp_file_hash.hash_sha512_hex].append(tmp_file_hash)
        except Exception as ex:
            logging.warning("FileHash failed: %s", ex)

    # Search through hash lists for lists with more than one hash
    # FIXME: Should the delete_safe path be referenced to the root_path?
    tmp_delete_safe_path = Path(args.delete_from) if args.delete_from else None
    logging.info("Duplicate Hash List Length: %d", len(FILE_HASH_LISTS))
    logging.debug("Delete Safe Path: %s", tmp_delete_safe_path)
    for item in FILE_HASH_LISTS:
        if len(FILE_HASH_LISTS[item]) > 1:
            logging.info("Duplicate Hash: %s", item)
            logging.info("   Count: %d", len(FILE_HASH_LISTS[item]))
            tmp_files_deleted = 0
            for file_hash in FILE_HASH_LISTS[item]:
                logging.info("   File: %s", file_hash.file_path)
                # If not deleting all of them and matches delete safe path
                if (tmp_files_deleted < (len(FILE_HASH_LISTS[item]) - 1)) and tmp_delete_safe_path in file_hash.file_path.parents:
                    tmp_files_deleted = tmp_files_deleted + 1
                    if args.dry:
                        logging.info("DRY RUN: NOT Deleting file: %s", file_hash.file_path)
                    else:
                        logging.info("Deleted file: %s", file_hash.file_path)
                        try:
                            file_hash.file_path.unlink()
                        except Exception as ex:
                            logging.warning("Error deleting file: %s", ex)
                    # Should add a check here to remove empty directories.

if __name__ == '__main__':
    main()
