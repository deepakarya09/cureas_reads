from http import HTTPStatus

from flask import request
from flask_restplus import Resource
from werkzeug.exceptions import abort
import time

from app.main.controllers import error_m
from app.main.utils.scrape_dto import ScrapDto
from app.main.services.scrape_service import get_data, generate_screnshot_of_element
from app.main.field_valiadators.api.api_scrape_schema_validator import PostScapeValidator
from app.main.config import driver

api = ScrapDto.api
req = ScrapDto.req_link

_validator = PostScapeValidator()


@api.route("api/v1.0/scrape")
class GetLink(Resource):
    @api.expect(req)
    def post(self):
        data = request.json
        error = _validator.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return get_data(data)


@api.route("api/v1.0/screenshot")
class GetdLink(Resource):
    def post(self):
        data = request.json
        return generate_screnshot_of_element(data)
