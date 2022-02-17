from http import HTTPStatus

from flask_restplus import Resource
from flask import request
from werkzeug.exceptions import abort

from app.main.controllers import error_m
from app.main.services.tags_service import get_all, tags
from app.main.tokenvalidation.token_check import token_required
from app.main.utils.tags_dto import tagDto
from app.main.field_valiadators.aapi.aapi_tags_schema_validator import TagSchemaValidator

api = tagDto.api
_req_tag = tagDto.req_tag
_res_all = tagDto.res_all
_res_tag = tagDto.res_tag

_tag = TagSchemaValidator()


@api.route("aapi/v1.0/tag")
class Tag(Resource):
    @api.expect(_req_tag)
    @api.marshal_with(_res_tag)
    @token_required
    def post(self):
        """insert tags"""
        data = request.json
        error = _tag.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return tags(data)


@api.route("aapi/v1.0/tags")
class GetAllTag(Resource):
    @api.marshal_with(_res_all)
    @token_required
    def get(self):
        return get_all()
