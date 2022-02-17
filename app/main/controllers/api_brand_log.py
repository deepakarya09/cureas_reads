from flask_restplus import Resource
from flask import request
from werkzeug.exceptions import abort
from app.main.controllers import error_m
from app.main.services.brand_logs_services import get_brand_logs
from app.main.tokenvalidation.token_check import token_required
from app.main.utils.api_brand_log_dto import BrandLogsDto

api = BrandLogsDto.api

_res_api_log = BrandLogsDto.res_brand_log


@api.route("api/v1.0/brand/<brand_id>/logs")
class BrandLogs(Resource):
    @api.marshal_with(_res_api_log)
    def get(self, brand_id):
        return get_brand_logs(brand_id)
