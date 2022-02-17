from http import HTTPStatus
from flask_restplus import Resource
from flask import request
from werkzeug.exceptions import abort
from flask import current_app as cur_app

from app.main.services.sapi_content_services import validation, get_all_contents,delete_content,update_content
from app.main.controllers import error_m
from app.main.tokenvalidation.token_check import token_required
from app.main.utils.sapi_content_dto import contentDto
from app.main.field_valiadators.sapi.sapi_content_schema_validator import SapiContentValidator

api = contentDto.api
_res_all_content = contentDto.res_all_content
_req_content = contentDto.req_content
_res_content = contentDto.res_content
_validator = SapiContentValidator()


@api.route("sapi/v1.0/content")
class SContent(Resource):
    @api.expect(_req_content)
    @api.marshal_with(_res_content)
    @token_required
    def post(self):
        data = request.json
        error = _validator.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return validation(data)


@api.route("sapi/v1.0/contents")
class SContent(Resource):
    @api.marshal_with(_res_all_content)
    @token_required
    def get(self):
        # URL?page=1&limit=2&searchKey=b8843kONRkxb9rvcvUhPHaF3
        args = request.args
        page = int(args.get('page', cur_app.config['PAGE']))
        limit = int(args.get('limit', cur_app.config['LIMIT']))
        searchKey = args.get('searchKey')
        return get_all_contents(page, limit, searchKey)


@api.route("sapi/v1.0/content/<id>")
class DeleteContent(Resource):
    @token_required
    def delete(self, id):
        return delete_content(id)

    @api.expect(_req_content)
    @api.marshal_with(_res_content)
    @token_required
    def put(self, id):
        data = request.json
        error = _validator.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return update_content(id,data)
