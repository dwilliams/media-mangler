#!/usr/bin/env python3

# This scanner will push directly to the database, not to the web server.

### IMPORTS ###
import argparse
import logging
import os

import mmangler.models

from pathlib import Path

from mmangler.utilities.pathwalker import PathWalker
from mmangler.utilities.filehash import FileHash
from mmangler.utilities.filemime import FileMime
from mmangler.utilities.mediadiscover import MediaDiscover

from mmangler.exceptions import ConflictException, MultipleResultsException, ServerErrorException

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class MediaPoster:
    def __init__(self, media_path):
        self.logger = logging.getLogger(type(self).__name__)
        self.path = Path(media_path)
        self.id = None
        self._media_discoverer = MediaDiscover(self.path)

    def post_to_db(self):
        self.logger.debug("Post to DB")
        try:
            # Look for name in database
            tmp_db_result = mmangler.models.MediaModel.query.filter_by(name=self._media_discoverer.name).one()
            self.logger.debug("Rows: %s", tmp_db_result)
            # FIXME: If name, check type and capacity
            #    if match, return ID
            #    else return error
            self.logger.debug("Found existing media: %s:%s", tmp_db_result.id, tmp_db_result.name)
            self.id = tmp_db_result.id
        except NoResultFound:
            # else add to DB and return ID
            tmp_new_media = mmangler.models.MediaModel(
                name = self._media_discoverer.name,
                media_type = self._media_discoverer.type.value,
                capacity_bytes = self._media_discoverer.capacity_bytes
            )
            tmp_session = mmangler.models.db_session()
            tmp_session.add(tmp_new_media)
            tmp_session.commit()
            self.logger.debug("Added new media: %s:%s", tmp_new_media.id, tmp_new_media.name)
            self.id = tmp_new_media.id
        except MultipleResultsFound:
            # Too many results, so error out
            self.logger.error("Too many results for media: name: %s", self._media_discoverer.name)
        except Exception as ex:
            # Something else is wrong, so bail out
            self.logger.error("Exception: %s", ex)

class FilePoster:
    def __init__(self, file_path, media_id):
        self.logger = logging.getLogger(type(self).__name__)
        self.path = Path(file_path)
        self.media_id = media_id
        self.id = None
        #self.name = os.path.splitext(os.path.basename(self.path))[0]
        self.name = self.path.stem
        self.size_bytes = os.stat(self.path).st_size
        self._filehash = FileHash(self.path)
        self._filemime = FileMime(self.path)

    def _insert_file(self, tmp_session):
        try:
            # Look up by hash in database
            #tmp_db_result = mmangler.models.FileModel.query.filter_by(hash_sha512_hex=tmp_post_body['hash_sha512_hex']).one()
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

    def _insert_mfa(self, tmp_session, tmp_media, tmp_file):
        try:
            tmp_mfa = mmangler.models.MediaFileAssociationModel(
                medias_id = tmp_media.id,
                file_path = os.path.splitdrive(os.path.dirname(self.path))[1], # grab the path part without the drive letter
                file_name = os.path.basename(self.path)
            )
            tmp_file.medias.append(tmp_mfa)
            #with mmangler.models.db_session() as tmp_session:
            tmp_session.add(tmp_file)
            tmp_session.commit()
            self.logger.debug("Updated file medias: %s:%s", tmp_file.id, tmp_file.metadata_name)
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
            tmp_media_result = tmp_session.query(mmangler.models.MediaModel).get(self.media_id)
            self.logger.debug("Medias: %s", tmp_media_result)
            # Try to insert the file into the database
            if self._insert_file(tmp_session):
                # File inserted
                logging.debug("File Inserted")
            else:
                # File already in DB
                logging.debug("File already there")
            # Try to add the media association
            # FIXME: Check if already associated
            tmp_file_result = tmp_session.query(mmangler.models.FileModel).filter_by(hash_sha512_hex=self._filehash.hash_sha512_hex).one()
            self.logger.debug("Resulting file medias: %s", [x.media for x in tmp_file_result.medias])
            if tmp_media_result not in [x.media for x in tmp_file_result.medias]:
                self._insert_mfa(tmp_session, tmp_media_result, tmp_file_result)
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
    parser.add_argument("--media_id", help="ID of media being scanned.  This is to override media discovery.")
    parser.add_argument("--mdiscv_type", help="Override the discovery of the media type.")
    parser.add_argument("media_root", help="Path to the media root to be scanned.  Usually will be a drive letter (e.g. D:\).")
    args = parser.parse_args()

    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    logging.basicConfig(
        format=log_format,
        level=(logging.DEBUG if args.verbose else logging.INFO)
    )

    logging.debug("Args: %s", args)
    mmangler.models.prepare_db("mysql+pymysql://{}:{}@{}:{}/{}".format(
        args.db_user, args.db_pass, args.db_host, args.db_port, args.db_name
    ), echo=False)

    tmp_path = Path(args.media_root)
    logging.info("Media Root: %s", tmp_path)

    if not args.media_id:
        # POST the media to the server and get back a media_id
        tmp_new_media = MediaPoster(media_path=tmp_path)
        if args.mdiscv_type:
            tmp_new_media.media_type = mmangler.models.MediaTypeEnum(args.mdiscv_type)
        if not args.dry:
            tmp_new_media.post_to_db()
        tmp_media_id = tmp_new_media.id
    else:
        tmp_media_id = args.media_id

    path_walker = PathWalker(tmp_path)

    tmp_file_counter = 0
    tmp_total_file_count = len(path_walker.files_list)
    for item in path_walker.files_list:
        tmp_file_counter = tmp_file_counter + 1
        logging.info("File Number: %d of %d", tmp_file_counter, tmp_total_file_count)
        tmp_file = FilePoster(item, tmp_media_id)
        if not args.dry:
            tmp_file.post_to_db()

if __name__ == '__main__':
    main()
