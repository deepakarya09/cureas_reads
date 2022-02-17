import distutils
from distutils import util
from flask_restplus import Resource
from flask import request
from app.main.services.template_css_style_services import delete_template_css_style, get_all_template_css_style, get_template_css_style, post_template_css_style, put_template_css_style
from app.main.utils.api_template_css_style import TemplateCssStyleAPI

api = TemplateCssStyleAPI.api
_res_all = TemplateCssStyleAPI.get_all_template_css
_get_response = TemplateCssStyleAPI.get_response_for_template_css
_post_request = TemplateCssStyleAPI.post_for_template_css
_put_request = TemplateCssStyleAPI.put_for_template_css
_delete_response = TemplateCssStyleAPI.delete_response


@api.route("api/v1.0/templatecssstyle")
class TemplateCssController(Resource):
    @api.expect(_post_request)
    @api.marshal_with(_get_response)
    def post(self):
        data = request.json
        return post_template_css_style(data)

    @api.marshal_with(_res_all)
    def get(self):
        return get_all_template_css_style()


@api.route("api/v1.0/templatecssstyle/<id>")
class TemplateCssControllerID(Resource):
    @api.marshal_with(_get_response)
    def get(self, id):
        return get_template_css_style(id)

    @api.marshal_with(_delete_response)
    def delete(self, id):
        return delete_template_css_style(id)

    @api.expect(_put_request)
    @api.marshal_with(_get_response)
    def put(self, id):
        data = request.json
        return put_template_css_style(id, data)
