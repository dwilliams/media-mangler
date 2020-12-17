#!/usr/bin/env python3

# This scanner will push directly to the database, not to the web server.

### IMPORTS ###
import argparse
import hashlib
import logging
import os

from pathlib import Path

from mmangler.utilities.pathwalker import PathWalker

### GLOBALS ###

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
    parser.add_argument("--dry", help="Dry run, don't delete files.", action="store_true")
    parser.add_argument("--delete_from", help = "Directory from which duplicates will be deleted.")
    parser.add_argument("--exclude_dirs", help = "Comma separated string of directories to exclude from scan.")
    parser.add_argument("--output_file", help = "File to output logging.")
    parser.add_argument("media_root", help="Path to the media root to be scanned.  Usually will be a drive letter (e.g. D:\).")
    args = parser.parse_args()

    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    if args.output_file:
        logging.basicConfig(
            format = log_format,
            level = (logging.DEBUG if args.verbose else logging.INFO),
            filename = args.output_file
        )
    else:
        logging.basicConfig(
            format = log_format,
            level = (logging.DEBUG if args.verbose else logging.INFO)
        )

    logging.debug("Args: %s", args)

    tmp_path = os.path.abspath(args.media_root)
    logging.info("Media Root: %s", tmp_path)

    # _filename_ignore = [
    #     'WPSettings.dat',
    #     'IndexerVolumeGuid'
    # ]
    #
    # tmp_filepath_list = []
    # for dirpath, dirnames, filenames in os.walk(tmp_path):
    #     for filename in filenames:
    #         if filename not in _filename_ignore:
    #             #tmp_filepath_list.append(os.path.join(dirpath, filename))
    #             tmp_filepath_list.append({'dirpath': dirpath, 'filename': filename})
    #             if len(tmp_filepath_list) % 99 == 0:
    #                 logging.info("Counted %d files", len(tmp_filepath_list))

    path_walker = PathWalker(tmp_path, args.exclude_dirs.split(',') if args.exclude_dirs else [])

    # Hash all of the files
    tmp_file_counter = 0
    for item in path_walker.files_list_dicts:
        tmp_file_counter = tmp_file_counter + 1
        logging.info("File Number: %d of %d", tmp_file_counter, len(path_walker.files_list_dicts))
        logging.debug("    Name: %s / %s", item['dirpath'], item['filename'])

        try:
            # Hash the file
            tmp_file_hash = FileHash(item['dirpath'], item['filename'])

            # Add file to hash list, creating list if needed
            if not tmp_file_hash.hash_sha512_hex in FILE_HASH_LISTS:
                logging.debug("Creating a new list for new hash")
                FILE_HASH_LISTS[tmp_file_hash.hash_sha512_hex] = []
            logging.debug("Adding hash: %s", tmp_file_hash.hash_sha512_hex)
            FILE_HASH_LISTS[tmp_file_hash.hash_sha512_hex].append(tmp_file_hash)
        except Exception as ex:
            logging.warning("FileHash failed: %s", ex)

    # Search through hash lists for lists with more than one hash
    #LIST_FOR_SORTING = []
    # FIXME: Should the delete_safe path be referenced to the root_path?
    tmp_delete_safe_path = Path(args.delete_from) if args.delete_from else None
    logging.debug("Delete Safe Path: %s", tmp_delete_safe_path)
    for item in FILE_HASH_LISTS:
        if len(FILE_HASH_LISTS[item]) > 1:
            logging.info("Duplicate Hash: %s", item)
            logging.info("   Count: %d", len(FILE_HASH_LISTS[item]))
            tmp_files_deleted = 0
            for file_hash in FILE_HASH_LISTS[item]:
                logging.info(file_hash.get_path_name())
                #LIST_FOR_SORTING.append(file_hash)
                # If not deleting all of them and matches delete safe path
                tmp_path = Path(os.path.join(file_hash.path, file_hash.name))
                if (tmp_files_deleted < len(FILE_HASH_LISTS[item]) - 1) and tmp_delete_safe_path in tmp_path.parents:
                    if args.dry:
                        logging.info("DRY RUN: NOT Deleting file: %s", tmp_path)
                    else:
                        logging.info("Deleted file: %s", tmp_path)
                        tmp_path.unlink()
                    # Should add a check here to remove empty directories.

    # # Sort by filename and Display the list
    # logging.info("SORTED BY FILE NAME:")
    # LIST_SORTED = sorted(LIST_FOR_SORTING, key = lambda i: i.name)
    # for file_hash in LIST_SORTED:
    #     logging.info(file_hash.get_path_name())

if __name__ == '__main__':
    main()
