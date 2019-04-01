#!/usr/bin/env python3

### IMPORTS ###
import json
import logging

import mmangler.models
import mmangler.schemas

#from sqlalchemy.orm import noload
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class MediasResource:
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(type(self).__name__)
        super().__init__(*args, **kwargs)

    def on_get(self, request, response):
        self.logger.debug("URL: %s", request.full_url)
        tmp_media_schema = mmangler.schemas.MediaSchema(many=True)
        tmp_results = mmangler.models.MediaModel.query.all()
        response.text = json.dumps(tmp_media_schema.dump(tmp_results).data)

    async def on_post(self, request, response):
        self.logger.debug("URL: %s", request.full_url)
        tmp_media_schema = mmangler.schemas.MediaSchema()
        tmp_post_body = await request.media()
        self.logger.debug("Contents: %s", tmp_post_body)
        try:
            # Look for name in database
            tmp_db_result = mmangler.models.MediaModel.query.filter_by(name=tmp_post_body['name']).one()
            self.logger.debug("Rows: %s", tmp_db_result)
            # TODO: If name, check type and capacity
            #    if match, return ID
            #    else return error
            self.logger.debug("Found existing media: %s:%s", tmp_db_result.id, tmp_db_result.name)
            #response.text = json.dumps(tmp_media_schema.dump(tmp_db_result).data)
            # Removing file list from result to save transfer
            tmp_data = tmp_media_schema.dump(tmp_db_result).data
            tmp_data.pop("files", None)
            response.text = json.dumps(tmp_data)
            response.status_code = 200
        except NoResultFound:
            # else add to DB and return ID
            tmp_new_media = mmangler.models.MediaModel(
                name = tmp_post_body['name'],
                media_type = tmp_post_body['media_type'],
                capacity_bytes = tmp_post_body['capacity_bytes']
            )
            tmp_session = mmangler.models.db_session()
            tmp_session.add(tmp_new_media)
            tmp_session.commit()
            self.logger.debug("Added new media: %s:%s", tmp_new_media.id, tmp_new_media.name)
            # Removing file list from result to save transfer
            tmp_data = tmp_media_schema.dump(tmp_new_media).data
            tmp_data.pop("files", None)
            response.text = json.dumps(tmp_data)
            response.status_code = 201
        except MultipleResultsFound:
            # Too many results, so error out
            response.status_code = 400
        except Exception as ex:
            # Something else is wrong, so bail out
            self.logger.debug("Exception: %s", ex)
            response.status_code = 500

class MediaIdResource:
    def on_get(self, request, response, *, media_id):
        tmp_media_schema = mmangler.schemas.MediaSchema()
        tmp_result = mmangler.models.MediaModel.query.get(media_id)
        response.text = json.dumps(tmp_media_schema.dump(tmp_result).data)
