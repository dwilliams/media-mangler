#!/usr/bin/env python3

### IMPORTS ###
import json
import logging

import mmangler.models
import mmangler.schemas

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class ConflictException(Exception):
    pass

class MultipleResultsException(Exception):
    pass

class ServerErrorException(Exception):
    pass

class FilesResource:
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(type(self).__name__)
        super().__init__(*args, **kwargs)

    def on_get(self, request, response):
        tmp_file_schema = mmangler.schemas.FileSchema(many=True)
        tmp_results = mmangler.models.FileModel.query.all()
        response.text = json.dumps(tmp_file_schema.dump(tmp_results).data)

    async def on_post(self, request, response):
        self.logger.debug("URL: %s", request.full_url)
        tmp_file_schema = mmangler.schemas.FileSchema()
        tmp_post_body = await request.media()
        self.logger.debug("Contents: %s", tmp_post_body)
        try:
            # Open DB Session
            tmp_session = mmangler.models.db_session()
            # Look up media by id in database
            #tmp_media_result = mmangler.models.MediaModel.query.get(tmp_post_body['media_id'])
            tmp_media_result = tmp_session.query(mmangler.models.MediaModel).get(tmp_post_body['media_id'])
            self.logger.debug("Medias: %s", tmp_media_result)
            # Try to insert the file into the database
            if self._insert_file(tmp_session, tmp_post_body):
                # File inserted
                response.status_code = 201
            else:
                # File already in DB
                response.status_code = 200
            # Try to add the media association
            # TODO: Check if already associated
            #tmp_file_result = mmangler.models.FileModel.query.filter_by(hash_sha512_hex=tmp_post_body['hash_sha512_hex']).one()
            tmp_file_result = tmp_session.query(mmangler.models.FileModel).filter_by(hash_sha512_hex=tmp_post_body['hash_sha512_hex']).one()
            self.logger.debug("Resulting file medias: %s", [x.media for x in tmp_file_result.medias])
            if tmp_media_result not in [x.media for x in tmp_file_result.medias]:
                self._insert_mfa(tmp_session, tmp_media_result, tmp_file_result)
        except NoResultFound as ex:
            # Media not found or File not found after insert
            self.logger.debug("NoResultFound: %s", ex)
            response.status_code = 412
            tmp_session.rollback()
        except ConflictException:
            response.status_code = 409
            tmp_session.rollback()
        except MultipleResultsException:
            response.status_code = 400
            tmp_session.rollback()
        except ServerErrorException:
            response.status_code = 500
            tmp_session.rollback()
        except Exception as ex:
            # Something else is wrong, so bail out
            self.logger.debug("Exception: %s", ex)
            response.status_code = 500
            tmp_session.rollback()
        finally:
            tmp_session.close()

    def _insert_file(self, tmp_session, tmp_post_body):
        try:
            # Look up by hash in database
            #tmp_db_result = mmangler.models.FileModel.query.filter_by(hash_sha512_hex=tmp_post_body['hash_sha512_hex']).one()
            tmp_db_result = tmp_session.query(mmangler.models.FileModel).filter_by(hash_sha512_hex=tmp_post_body['hash_sha512_hex']).one()
            self.logger.debug("Rows: %s", tmp_db_result)
            # Check if name and size match (check type?)
            if tmp_db_result.name == tmp_post_body['name'] and tmp_db_result.size_bytes == tmp_post_body['size_bytes']:
                # On match, update relations, return 200
                self.logger.debug("Found existing file: %s:%s", tmp_db_result.id, tmp_db_result.name)
                return False
            else:
                # On miss, return 409
                self.logger.debug("Conflict: %s and %s", tmp_db_result.name, tmp_post_body['name'])
                raise ConflictException()
        except NoResultFound:
            # else add to DB and return ID/Object
            tmp_new_file = mmangler.models.FileModel(
                name = tmp_post_body['name'],
                file_type = tmp_post_body['file_type'],
                size_bytes = tmp_post_body['size_bytes'],
                hash_sha512_hex = tmp_post_body['hash_sha512_hex']
            )
            # tmp_session = mmangler.models.db_session()
            tmp_session.add(tmp_new_file)
            tmp_session.commit()
            self.logger.debug("Added new file: %s:%s", tmp_new_file.id, tmp_new_file.name)
            return True
        except MultipleResultsFound as ex:
            # Too many results, so error out
            self.logger.debug("MultipleResultsFound: %s", ex)
            raise MultipleResultsException()
        except Exception as ex:
            # Something else is wrong, so bail out
            self.logger.debug("Exception: %s", ex)
            raise ServerErrorException()

    def _insert_mfa(self, tmp_session, tmp_media, tmp_file):
        try:
            tmp_mfa = mmangler.models.MediaFileAssociationModel(
                medias_id = tmp_media.id
            )
            tmp_file.medias.append(tmp_mfa)
            #with mmangler.models.db_session() as tmp_session:
            tmp_session.add(tmp_file)
            tmp_session.commit()
            self.logger.debug("Updated file medias: %s:%s", tmp_file.id, tmp_file.name)
        except Exception as ex:
            # Something else is wrong, so bail out
            self.logger.debug("Exception: %s", ex)
            raise ServerErrorException()

class FileIdResource:
    def on_get(self, request, response, *, file_id):
        tmp_file_schema = mmangler.schemas.FileSchema()
        tmp_result = mmangler.models.FileModel.query.get(file_id)
        response.text = json.dumps(tmp_file_schema.dump(tmp_result).data)
