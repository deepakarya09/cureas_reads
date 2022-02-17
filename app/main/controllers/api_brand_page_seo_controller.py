from flask_restplus import Resource
from flask import request
from werkzeug.exceptions import abort
from app.main.controllers import error_m
from app.main.services.pages.page_seo_services import get_page_seo, save_page_seo, update_page_seo
from app.main.tokenvalidation.token_check import token_required
from app.main.utils.api_page_seo_dto import BrandPageSeoDto
from http import HTTPStatus

api = BrandPageSeoDto.api

_res_api_content = BrandPageSeoDto.seo_response
_req_api_content = BrandPageSeoDto.seo_request


@api.route("api/v1.0/seo/page/<page_id>")
class Content(Resource):
    @api.expect(_req_api_content)
    @api.marshal_with(_res_api_content)
    # @token_required
    def post(self, page_id):
        data = request.json
        return save_page_seo(page_id, data)

    @api.expect(_req_api_content)
    @api.marshal_with(_res_api_content)
    def put(self, page_id):
        data = request.json
        return update_page_seo(page_id, data)

    @api.marshal_with(_res_api_content)
    def get(self, page_id):
        return get_page_seo(page_id)
