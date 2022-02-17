from http import HTTPStatus
from flask_restplus import Resource
from flask import request
from flask import current_app as cur_app
from werkzeug.exceptions import abort
from app.main.services.source_services import source_get, add_source, update_source, get_specific_source, delete_source
from app.main.controllers import error_m
from app.main.tokenvalidation.token_check import token_required
from app.main.utils.source_dto import SourceDto
from app.main.field_valiadators.aapi.aapi_source_schema_validator import PostSourceSchemaValidator, \
    PutSourceSchemaValidator

api = SourceDto.api

_req_source = SourceDto.req_source
_res_sources = SourceDto.res_sources
_req_for_put = SourceDto.req_for_put
_res_source = SourceDto.res_source
post_validator = PostSourceSchemaValidator()
put_validator = PutSourceSchemaValidator()


@api.route("aapi/v1.0/source")
class Sources(Resource):
    @api.expect(_req_source)
    @api.marshal_with(_res_source)
    @token_required
    def post(self):
        """Insert source"""
        data = request.json
        error = post_validator.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return add_source(data)


@api.route("aapi/v1.0/source/<source_id>")
class PutSource(Resource):
    @api.expect(_req_for_put)
    @api.marshal_with(_res_source)
    @token_required
    def put(self, source_id):
        data = request.json
        error = put_validator.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return update_source(source_id, data)

    @api.marshal_with(_res_source)
    @token_required
    def get(self, source_id):
        return get_specific_source(source_id)


@api.route("aapi/v1.0/sources")
class Sources(Resource):
    @api.marshal_with(_res_sources)
    @token_required
    def get(self):
        """Get all Sources information"""
        # URL?page=1&limit=2&searchKey=b8843kONRkxb9rvcvUhPHaF3
        args = request.args
        page = int(args.get('page', cur_app.config["PAGE"]))
        limit = int(args.get('limit', cur_app.config["LIMIT"]))
        searchKey = args.get('searchKey')
        return source_get(page, limit, searchKey)


@api.route("aapi/v1.0/source/<id>")
class DeleteSource(Resource):
    @token_required
    def delete(self, id):
        return delete_source(id)
