from flask_restplus import Resource
from flask import request
from werkzeug.exceptions import abort
from app.main.controllers import error_m
from app.main.services.analytics.analytics_social import get_anylitics_by_sharing_id, social_analytics
from app.main.tokenvalidation.token_check import token_required
from app.main.utils.api_social_analytics_dto import SocialAnalyticsDto

api = SocialAnalyticsDto.api

_res_api_log = SocialAnalyticsDto.res_social_analytics
_res_api_log_by_id = SocialAnalyticsDto.res_social_analytics_by_id


@api.route("api/v1.0/brand/<brand_id>/social/analytics")
class BrandLogs(Resource):
    @api.marshal_with(_res_api_log)
    def get(self, brand_id):
        args = request.args
        interval = args.get('interval')
        return social_analytics(brand_id, interval)


@api.route("api/v1.0/social/analytics/<sharing_id>")
class BrandLogs(Resource):
    @api.marshal_with(_res_api_log_by_id)
    def get(self, sharing_id):
        return get_anylitics_by_sharing_id(sharing_id)
