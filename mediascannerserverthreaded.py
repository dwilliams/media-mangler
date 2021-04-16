#!/usr/bin/env python3

# This scanner will push directly to the database, not to the web server.

### IMPORTS ###
import argparse
import logging
import os
import sys
import win32api

import queue
import signal
import threading

import mmangler.models

from pathlib import Path

from mmangler.utilities.pathwalker import PathWalker
from mmangler.utilities.filehash import FileHash
from mmangler.utilities.filemime import FileMime

from mmangler.exceptions import ConflictException, MultipleResultsException, ServerErrorException

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class ServerSharePoster:
    def __init__(self, share_path):
        self.logger = logging.getLogger(type(self).__name__)
        self.path = Path(share_path)
        self.id = 0;
        # FIXME: Make this work for both winderps and loonix
        self.name = win32api.GetVolumeInformation(str(self.path))[0]
        self.logger.info("Media Label: %s", self.name)

    def post_to_db(self):
        self.logger.debug("Post to DB")
        try:
            # Look for share name in database
            tmp_db_result = mmangler.models.ServerShareModel.query.filter_by(name=self.name).one()
            self.logger.debug("Rows: %s", tmp_db_result)
            self.logger.debug("Found existing media: %s:%s", tmp_db_result.id, tmp_db_result.name)
            self.id = tmp_db_result.id
        except NoResultFound:
            # else add to DB and return ID
            tmp_new_share = mmangler.models.ServerShareModel(name = self.name)
            tmp_session = mmangler.models.db_session()
            tmp_session.add(tmp_new_share)
            tmp_session.commit()
            self.logger.debug("Added new media: %s:%s", tmp_new_share.id, tmp_new_share.name)
            self.id = tmp_new_share.id
        except MultipleResultsFound:
            # Too many results, so error out
            self.logger.error("Too many results for media: name: %s", self.name)
        except Exception as ex:
            # Something else is wrong, so bail out
            self.logger.error("Exception: %s", ex)

class ServerFilePoster:
    def __init__(self, file_path, share_id, stop_event = threading.Event()):
        self.logger = logging.getLogger(type(self).__name__)
        self.path = Path(file_path)
        self.share_id = share_id
        self.id = None
        self.name = self.path.stem
        self.size_bytes = os.stat(self.path).st_size
        self._stop_event = stop_event # Needed to allow breaking out of hashing loop early on a CTRL+C
        self._stop_event.clear()
        self._filehash = FileHash(self.path, stop_event = self._stop_event)
        self._filemime = FileMime(self.path)

    # FIXME: Should probably make this lookup the file data from the server on instantiation of this class
    def _insert_file(self, tmp_session):
        try:
            # Look up by hash in database
            tmp_db_result = tmp_session.query(mmangler.models.FileModel).filter_by(hash_sha512_hex=self._filehash.hash_sha512_hex).one()
            self.logger.debug("Rows: %s", tmp_db_result)
            # Check if name and size match (check type?)
            if tmp_db_result.hash_md5_hex == self._filehash.hash_md5_hex and tmp_db_result.size_bytes == self.size_bytes:
                # On match, update relations, return 200
                self.logger.debug("Found existing file: %s:%s", tmp_db_result.id, tmp_db_result.metadata_name)
                return False
            else:
                # On miss, return 409
                self.logger.debug("Conflict: %s and %s", tmp_db_result.metadata_name, self.name)
                raise ConflictException()
        except NoResultFound:
            # else add to DB and return ID/Object
            tmp_new_file = mmangler.models.FileModel(
                metadata_name = self.name,
                file_type = self._filemime.type.value,
                size_bytes = self.size_bytes,
                hash_sha512_hex = self._filehash.hash_sha512_hex,
                hash_md5_hex = self._filehash.hash_md5_hex
            )
            # tmp_session = mmangler.models.db_session()
            tmp_session.add(tmp_new_file)
            tmp_session.commit()
            self.logger.debug("Added new file: %s:%s", tmp_new_file.id, tmp_new_file.metadata_name)
            return True
        except MultipleResultsFound as ex:
            # Too many results, so error out
            self.logger.error("MultipleResultsFound: %s", ex)
            raise MultipleResultsException()
        except Exception as ex:
            # Something else is wrong, so bail out
            self.logger.error("Exception: %s", ex)
            raise ServerErrorException()

    def _insert_mfa(self, tmp_session, tmp_share, tmp_file):
        try:
            tmp_ssfa = mmangler.models.ServerShareFileAssociationModel(
                servershares_id = tmp_share.id,
                file_path = os.path.splitdrive(os.path.dirname(self.path))[1], # grab the path part without the drive letter
                file_name = os.path.basename(self.path)
            )
            tmp_file.servershares.append(tmp_ssfa)
            #with mmangler.models.db_session() as tmp_session:
            tmp_session.add(tmp_file)
            tmp_session.commit()
            self.logger.debug("Updated file servershares: %s:%s", tmp_file.id, tmp_file.metadata_name)
        except Exception as ex:
            # Something else is wrong, so bail out
            self.logger.debug("Exception: %s", ex)
            raise ServerErrorException()

    def post_to_db(self):
        self.logger.debug("Post to DB")
        try:
            # Open DB Session
            tmp_session = mmangler.models.db_session()
            # Look up media by id in database
            tmp_share_result = tmp_session.query(mmangler.models.ServerShareModel).get(self.share_id)
            self.logger.debug("Server Share: %s", tmp_share_result)
            # Try to insert the file into the database
            if self._insert_file(tmp_session):
                # File inserted
                logging.debug("File Inserted")
            else:
                # File already in DB
                logging.debug("File already there")
            # Try to add the media association
            tmp_file_result = tmp_session.query(mmangler.models.FileModel).filter_by(hash_sha512_hex=self._filehash.hash_sha512_hex).one()
            self.logger.debug("Resulting file servershares: %s", [x.servershare for x in tmp_file_result.servershares])
            if tmp_share_result not in [x.servershare for x in tmp_file_result.servershares]:
                self._insert_mfa(tmp_session, tmp_share_result, tmp_file_result)
        except NoResultFound as ex:
            # Media not found or File not found after insert
            self.logger.error("NoResultFound: %s", ex)
            tmp_session.rollback()
        except ConflictException as ex:
            self.logger.error("ConflictException: %s", ex)
            tmp_session.rollback()
        except MultipleResultsException as ex:
            self.logger.error("MultipleResultsException: %s", ex)
            tmp_session.rollback()
        except ServerErrorException as ex:
            self.logger.error("ServerErrorException: %s", ex)
            tmp_session.rollback()
        except Exception as ex:
            # Something else is wrong, so bail out
            self.logger.error("Exception: %s", ex)
            tmp_session.rollback()
        finally:
            tmp_session.close()

class PathWalkerThread(threading.Thread):
    def __init__(self, file_list_queue, pw_done_event, path):
        # Ensure the parent's __init__ is called
        super().__init__()
        self.logger = logging.getLogger(type(self).__name__)
        self._shutdown_now = threading.Event()
        self._shutdown_now.clear()

        self.file_list_queue = file_list_queue
        self.pw_done_event = pw_done_event
        self.path = Path(path)

    def shutdown_now(self):
        self.logger.debug("Shutdown Now")
        self._shutdown_now.set()

    def run(self):
        self.logger.info("Starting Thread")
        # FIXME: Need to make this smart enough to bail out early.
        path_walker = PathWalker(self.path, stop_event = self._shutdown_now)

        self.logger.info("Total File Count: %d", len(path_walker.files_list))
        for item in path_walker.files_list:
            # Shutdown quickly
            if(self._shutdown_now.is_set()):
                self.logger.warning("Stopping Early")
                break
            self.file_list_queue.put(item)
        self.pw_done_event.set()
        self.logger.info("Ending Thread")

class FileScannerAndPosterThread(threading.Thread):
    def __init__(self, file_list_queue, pw_done_event, server_share, dry_run = False):
        # Ensure the parent's __init__ is called
        super().__init__()
        self.logger = logging.getLogger(type(self).__name__)
        self._shutdown_now = threading.Event()
        self._shutdown_now.clear()

        self.file_list_queue = file_list_queue
        self.pw_done_event = pw_done_event
        self.server_share = server_share
        self.dry_run = dry_run

    def shutdown_now(self):
        self.logger.debug("Shutdown Now")
        self._shutdown_now.set()

    def run(self):
        self.logger.info("Starting Thread")
        # If there something in the queue (not empty) or if the path walker is not done:
        tmp_file_proc_count = 0
        while(not self._shutdown_now.is_set()):
            try:
                if self.file_list_queue.empty() and self.pw_done_event.is_set():
                    self.logger.info("Empty queue and no more items coming")
                    break
                tmp_file_path = self.file_list_queue.get_nowait()
                tmp_file = ServerFilePoster(tmp_file_path, self.server_share.id, stop_event = self._shutdown_now)
                # FIXME: Figure out a better way to handle the DRY-RUN flag / posting to DB
                if not self.dry_run:
                   tmp_file.post_to_db()
                tmp_file_proc_count = tmp_file_proc_count + 1
                self.logger.debug("Processed %d files in this thread", tmp_file_proc_count)
            except:
                pass
        self.logger.info("Ending Thread")

### MAIN ###
def main():
    parser = argparse.ArgumentParser(description="Scan and hash files on media, then push into the database.")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--dry", help="Dry run, don't push to database.", action="store_true")
    parser.add_argument("--db_user", default = "root", help="Set the database username.")
    parser.add_argument("--db_pass", default = "password", help="Set the database password.")
    parser.add_argument("--db_host", default = "localhost", help="Set the database hostname.")
    parser.add_argument("--db_port", default = "3306", help="Set the database network port.")
    parser.add_argument("--db_name", default = "mediamangler", help="Set the database name.")
    parser.add_argument("--share_id", help="ID of share being scanned.  This is to override share discovery.")
    parser.add_argument("--output_file", help = "File to output logging.")
    parser.add_argument("share_root", help="Path to the share root to be scanned.  This will be a drive letter (e.g. D:\).")
    args = parser.parse_args()

    log_format = "%(asctime)s:%(levelname)s:%(threadName)s:%(name)s.%(funcName)s: %(message)s"
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

    logging.debug("Args: %s", args)
    # FIXME: Make this work better (helper function in models?):
    #        - Pull from environs (DB_URL and Separate Values)
    #        - Pull from args (DB_URL and Separate Values)
    mmangler.models.prepare_db("mysql+pymysql://{}:{}@{}:{}/{}".format(
        args.db_user, args.db_pass, args.db_host, args.db_port, args.db_name
    ), echo=False)

    tmp_path = Path(args.share_root)
    logging.info("Server Share Root: %s", tmp_path)

    # FIXME: This logic should be moved to the SharePoster class.
    #        The share_id logic should be moved into the class too.
    tmp_new_share = None
    if not args.share_id:
        # POST the media to the server and get back a media_id
        tmp_new_share = ServerSharePoster(share_path=tmp_path)
        if not args.dry:
            tmp_new_share.post_to_db()
        tmp_share_id = tmp_new_share.id
    else:
        tmp_share_id = args.share_id

    # Create the threads
    file_list_queue = queue.SimpleQueue()
    pathwalk_done_event = threading.Event()
    pathwalk_done_event.clear()
    thread_list = []
    thread_list.append(PathWalkerThread(file_list_queue, pathwalk_done_event, tmp_path))
    for i in range(3):
        thread_list.append(FileScannerAndPosterThread(file_list_queue, pathwalk_done_event, tmp_new_share, args.dry))

    try:
        # Start the threads
        for item in thread_list:
            item.start()
        # Wait for the threads to finish
        for item in thread_list:
            while item.is_alive():
                item.join(1)
    except KeyboardInterrupt:
        signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore extra CTRL+C presses as they make the exception unhappy
        # Tell all of the threads to shutdown
        for item in thread_list:
            item.shutdown_now()
        # Wait for the threads to shutdown
        for item in thread_list:
            while item.is_alive():
                item.join(1)

    # path_walker = PathWalker(tmp_path)
    #
    # # FIXME: Will we get a performance increase from threading this?  This is generally going to be limited by the
    # #        server's disk and network.
    # tmp_file_counter = 0
    # tmp_total_file_count = len(path_walker.files_list)
    # for item in path_walker.files_list:
    #     tmp_file_counter = tmp_file_counter + 1
    #     logging.info("File Number: %d of %d", tmp_file_counter, tmp_total_file_count)
    #     tmp_file = ServerFilePoster(item, tmp_share_id)
    #     if not args.dry:
    #         tmp_file.post_to_db()

    # FIXME: Should there be a cleanup cycle here to remove files that haven't been seen in X number of days?
    #        I.E. Remove old ServerShareFileAssociations to show the files aren't in the share anymore.

if __name__ == '__main__':
    main()
