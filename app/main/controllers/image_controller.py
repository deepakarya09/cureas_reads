from app.main.services.image_upload_services import image_byte
from app.main.utils.image_dto import ImageDto
from http import HTTPStatus

from flask import request
from flask_restplus import Resource
from werkzeug.exceptions import abort

from app.main.controllers import error_m

api = ImageDto.api

_req_image_link = ImageDto.req_image_link

_res_image_data = ImageDto.res_image_data


@api.route("api/v1.0/image/data")
class WidgetReplace(Resource):
    @api.expect(_req_image_link)
    @api.marshal_with(_res_image_data)
    def post(self):
        return image_byte(data=request.json)