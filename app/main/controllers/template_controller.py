from app.main.field_valiadators.api.api_template_validator import TemplateValidator
from app.main.field_valiadators.aapi.aapi_source_schema_validator import PostSourceSchemaValidator, \
    PutSourceSchemaValidator
from http import HTTPStatus
from flask_restplus import Resource
from flask import current_app as cur_app
from flask import request
from app.main.utils.template_dto import TemplateDto
from app.main.services.template_services import delete_template, post_template, get_all, update_template, get_by_id
from werkzeug.exceptions import abort
from app.main.controllers import error_m

api = TemplateDto.api

_request_template = TemplateDto.request_template
_response_template = TemplateDto.response_template
_response_all = TemplateDto.response_all
_validator = TemplateValidator()


@api.route("api/v1.0/template")
class template_cont(Resource):
    @api.expect(_request_template)
    @api.marshal_with(_response_template)
    def post(self):
        """Template"""
        data = request.json
        error = _validator.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return post_template(data)


@api.route("api/v1.0/templates")
class GetAllTemplate(Resource):
    @api.marshal_with(_response_all)
    def get(self):
        args = request.args
        category = args.get('category')
        page = int(args.get('page', cur_app.config['PAGE']))
        limit = int(args.get('limit', cur_app.config['LIMIT']))
        return get_all(category,page,limit)


@api.route("api/v1.0/template/<id>")
class DeleteContent(Resource):
    def delete(self, id):
        return delete_template(id)

    @api.marshal_with(_response_template)
    def get(self, id):
        return get_by_id(id)

    @api.expect(_request_template)
    @api.marshal_with(_response_template)
    def put(self, id):
        data = request.json
        error = _validator.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return update_template(id, data)
