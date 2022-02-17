from app.main.field_valiadators.api.api_story_template_validate import StoryTemplateValidator
from app.main.field_valiadators.aapi.aapi_source_schema_validator import PostSourceSchemaValidator, \
    PutSourceSchemaValidator
from http import HTTPStatus
from flask_restplus import Resource
from flask import current_app as cur_app
from flask import request
from app.main.services.story.story_template_services import delete_story_template, get_all_story_template, get_story_template_by_id, post_story_template, update_story_template
from app.main.utils.story_template_dto import StoryTemplateDto
from werkzeug.exceptions import abort
from app.main.controllers import error_m

api = StoryTemplateDto.api

_request_template = StoryTemplateDto.request_template_story
_response_template = StoryTemplateDto.response_template_story
_response_all = StoryTemplateDto.response_all_story_template
_validator = StoryTemplateValidator()


@api.route("api/v1.0/story_template")
class template_cont(Resource):
    @api.expect(_request_template)
    @api.marshal_with(_response_template)
    def post(self):
        """Story Template"""
        data = request.json
        error = _validator.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return post_story_template(data)


@api.route("api/v1.0/story_templates")
class GetAllTemplate(Resource):
    @api.marshal_with(_response_all)
    def get(self):
        args = request.args
        category = args.get('category')
        page = int(args.get('page', cur_app.config['PAGE']))
        limit = int(args.get('limit', cur_app.config['LIMIT']))
        return get_all_story_template(category, page, limit)


@api.route("api/v1.0/story_template/<id>")
class DeleteContent(Resource):
    def delete(self, id):
        return delete_story_template(id)

    @api.marshal_with(_response_template)
    def get(self, id):
        return get_story_template_by_id(id)

    @api.expect(_request_template)
    @api.marshal_with(_response_template)
    def put(self, id):
        data = request.json
        error = _validator.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return update_story_template(id, data)
