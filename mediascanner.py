#!/usr/bin/env python3

# This scanner will push directly to the database, not to the web server.

### IMPORTS ###
import argparse
import enum
import hashlib
import logging
import os
import psutil
import win32api

#import magic
from winmagic import magic

import mmangler.models

from mmangler.exceptions import ConflictException, MultipleResultsException, ServerErrorException

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

### GLOBALS ###
#DB_URL = "mysql+pymysql://root:password@localhost:3306/mediamangler"

### FUNCTIONS ###

### CLASSES ###
class MediaPoster:
    def __init__(self, media_path = None):
        self.logger = logging.getLogger(type(self).__name__)
        self.path = media_path
        self.id = None
        self.name = None
        self.media_type = None
        self.capacity_bytes = 0

        # If the media path is set, perform media discovery.
        if media_path is not None:
            self._media_discover()

    def _media_discover(self):
        self.logger.debug("Discovering Media")
        self.name = win32api.GetVolumeInformation(self.path)[0]
        self.logger.info("Media Label: %s", self.name)

        tmp_disk_usage = psutil.disk_usage(self.path)
        self.capacity_bytes = tmp_disk_usage.total
        self.logger.debug("Media Size: %d", tmp_disk_usage.total)

        tmp_disk_parts = psutil.disk_partitions()
        tmp_disk_part = next(x for x in tmp_disk_parts if os.path.abspath(x.device) == self.path)
        if tmp_disk_part.fstype in ["NTFS", "FAT", "FAT32"]:
            #self.media_type = MediaTypeEnum.HDD
            self.media_type = mmangler.models.MediaTypeEnum.HDD
        elif (tmp_disk_part.fstype in ["CDFS"]) or ("cdrom" in tmp_disk_part.opts):
            if self.capacity_bytes < 737148928: # 703 MiB (CD-R)
                self.media_type = mmangler.models.MediaTypeEnum.CD
            elif self.capacity_bytes < 8547991552: # 8.5 GiB (DVD-R DL)
                self.media_type = mmangler.models.MediaTypeEnum.DVD
            else:
                self.media_type = mmangler.models.MediaTypeEnum.BR
        self.logger.debug("Media Type: %s", self.media_type)

    def post_to_db(self):
        self.logger.debug("Post to DB")
        try:
            # Look for name in database
            tmp_db_result = mmangler.models.MediaModel.query.filter_by(name=self.name).one()
            self.logger.debug("Rows: %s", tmp_db_result)
            # TODO: If name, check type and capacity
            #    if match, return ID
            #    else return error
            self.logger.debug("Found existing media: %s:%s", tmp_db_result.id, tmp_db_result.name)
            self.id = tmp_db_result.id
        except NoResultFound:
            # else add to DB and return ID
            tmp_new_media = mmangler.models.MediaModel(
                name = self.name,
                media_type = self.media_type.value,
                capacity_bytes = self.capacity_bytes
            )
            tmp_session = mmangler.models.db_session()
            tmp_session.add(tmp_new_media)
            tmp_session.commit()
            self.logger.debug("Added new media: %s:%s", tmp_new_media.id, tmp_new_media.name)
            self.id = tmp_new_media.id
        except MultipleResultsFound:
            # Too many results, so error out
            self.logger.error("Too many results for media: name: %s", self.name)
        except Exception as ex:
            # Something else is wrong, so bail out
            self.logger.error("Exception: %s", ex)

class FilePoster:
    _mime_overrides = {
        "text/x-python": mmangler.models.FileTypeEnum.other
    }

    def __init__(self, file_path, media_id):
        self.logger = logging.getLogger(type(self).__name__)
        self.path = file_path
        self.media_id = media_id
        self.id = None
        self.name = os.path.splitext(os.path.basename(self.path))[0]
        self.file_type = None
        self.size_bytes = os.stat(self.path).st_size
        self._chunk_size = 65536
        self._hash_sha512 = hashlib.sha512()
        self._hash_md5 = hashlib.md5()
        # ...
        self._hashfile()
        self._mimefile()

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

    def _mimefile(self):
        tmp_mime = magic.Magic(mime=True)
        self.logger.debug("Path: %s", self.path)
        tmp_mimetype = tmp_mime.from_file(self.path)
        self.logger.debug("Mime Type: %s", tmp_mimetype)
        self.file_type = mmangler.models.FileTypeEnum.other
        if tmp_mimetype in self._mime_overrides.keys():
            self.file_type = self._mime_overrides[tmp_mimetype]
        elif tmp_mimetype.startswith("video"):
            self.file_type = mmangler.models.FileTypeEnum.video
        elif tmp_mimetype.startswith("audio"):
            self.file_type = mmangler.models.FileTypeEnum.audio
        elif tmp_mimetype.startswith("image"):
            self.file_type = mmangler.models.FileTypeEnum.photo
        elif tmp_mimetype.startswith("text"):
            self.file_type = mmangler.models.FileTypeEnum.text
        self.logger.debug("File Type: %s", self.file_type)

    def _get_dict_for_post(self):
        return {
            "metadata_name": self.name,
            "file_type": self.file_type.value,
            "size_bytes": self.size_bytes,
            "hash_sha512_hex": self.hash_sha512_hex,
            "hash_md5_hex": self.hash_md5_hex,
            "media_id": self.media_id
        }

    def _insert_file(self, tmp_session):
        try:
            # Look up by hash in database
            #tmp_db_result = mmangler.models.FileModel.query.filter_by(hash_sha512_hex=tmp_post_body['hash_sha512_hex']).one()
            tmp_db_result = tmp_session.query(mmangler.models.FileModel).filter_by(hash_sha512_hex=self.hash_sha512_hex).one()
            self.logger.debug("Rows: %s", tmp_db_result)
            # Check if name and size match (check type?)
            if tmp_db_result.hash_md5_hex == self.hash_md5_hex and tmp_db_result.size_bytes == self.size_bytes:
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
                file_type = self.file_type.value,
                size_bytes = self.size_bytes,
                hash_sha512_hex = self.hash_sha512_hex,
                hash_md5_hex = self.hash_md5_hex
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
            # TODO: Check if already associated
            tmp_file_result = tmp_session.query(mmangler.models.FileModel).filter_by(hash_sha512_hex=self.hash_sha512_hex).one()
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

    tmp_path = os.path.abspath(args.media_root)
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
        tmp_file = FilePoster(item, tmp_media_id)
        if not args.dry:
            tmp_file.post_to_db()

if __name__ == '__main__':
    main()
