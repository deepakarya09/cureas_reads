import distutils
from distutils import util
from flask_restplus import Resource
from flask import request
from app.main.services.css_style_services import delete_css_style, get_all_css_style, get_all_css_style_by_name, get_css_style, post_css_style, put_css_style
from app.main.utils.api_css_style import CssStyleAPI

api = CssStyleAPI.api
_res_all = CssStyleAPI.get_all_css_style
_get_response = CssStyleAPI.get_response_for_css_style
_post_request = CssStyleAPI.post_for_css_style
_put_request = CssStyleAPI.put_for_css_style
_delete_response = CssStyleAPI.delete_response
_res_all_by_name = CssStyleAPI.get_all_css_style_by_template_css_name


@api.route("api/v1.0/cssstyle")
class CssController(Resource):
    @api.expect(_post_request)
    @api.marshal_with(_get_response)
    def post(self):
        data = request.json
        return post_css_style(data)

    @api.marshal_with(_res_all)
    def get(self):
        return get_all_css_style()


@api.route("api/v1.0/cssstyle/<id>")
class CssControllerID(Resource):
    @api.marshal_with(_get_response)
    def get(self, id):
        return get_css_style(id)

    @api.marshal_with(_delete_response)
    def delete(self, id):
        return delete_css_style(id)

    @api.expect(_put_request)
    @api.marshal_with(_get_response)
    def put(self, id):
        data = request.json
        return put_css_style(id, data)


@api.route("api/v1.0/allcssstyle/<name>")
class CssControllerAll(Resource):
    @api.marshal_with(_res_all_by_name)
    def get(self, name):
        return get_all_css_style_by_name(name)
