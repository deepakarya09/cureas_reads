from app.main.services.parser_service import widget_replace, widget_parse
from app.main.utils.parser_dto import ParserDTO
from flask_restplus import Resource
from flask import request

api = ParserDTO.api

_req_page_replace = ParserDTO.req_page_replace

_res_page_replace = ParserDTO.res_parser


@api.route("api/v1.0/brand/widget/replace")
class WidgetReplace(Resource):
    @api.expect(_req_page_replace)
    @api.marshal_with(_res_page_replace)
    def post(self):
        return widget_replace(data=request.json)


@api.route("api/v1.0/brand/<brand_id>/widget/<widget_name>")
class WidgetImage(Resource):
    def post(self, brand_id, widget_name):
        return widget_parse(brand_id=brand_id, widget_name=widget_name, data=request.json)
