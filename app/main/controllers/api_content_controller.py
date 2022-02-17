from flask_restplus import Resource
from flask import request
from werkzeug.exceptions import abort
from flask import current_app as cur_app
from app.main.services.api_content_services import save_content, get_all, delete_content
from app.main.controllers import error_m
from app.main.tokenvalidation.token_check import token_required
from app.main.utils.api_content_dto import api_contentDto
from app.main.field_valiadators.api.api_content_schema_validator import apiContentValidator
from http import HTTPStatus

api = api_contentDto.api

_res_all_api_content = api_contentDto.res_all_api_content
_req_api_content = api_contentDto.req_api_content
_res_api_content = api_contentDto.res_api_content
_post_validator = apiContentValidator()


@api.route("api/v1.0/content")
class Content(Resource):
    @api.expect(_req_api_content)
    @api.marshal_with(_res_api_content)
    @token_required
    def post(self):
        data = request.json
        error = _post_validator.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return save_content(data)


@api.route("api/v1.0/contents/")
class Content(Resource):
    @api.marshal_with(_res_all_api_content)
    @token_required
    def get(self):
        args = request.args
        page = int(args.get('page', cur_app.config["PAGE"]))
        limit = int(args.get('limit', cur_app.config["LIMIT"]))
        return get_all(page, limit)


@api.route("api/v1.0/content/<id>")
class DeleteContent(Resource):
    @token_required
    def delete(self, id):
        return delete_content(id)
