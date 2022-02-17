from flask_restplus import Resource
from flask import request
from werkzeug.exceptions import abort
from app.main.controllers import error_m
from app.main.services.analytics.analytics_content import graph_analytics, kafka_consumer, producer_kafka, recent_published_content_pages, recent_published_content_storys, total_views_content
from app.main.services.analytics.analytics_social import get_anylitics_by_sharing_id, social_analytics
from app.main.tokenvalidation.token_check import token_required
from app.main.utils.api_analytics_content_dto import AnalyticsContentDto
from flask import current_app as cur_app
api = AnalyticsContentDto.api

_req_api = AnalyticsContentDto.req_kafka
_res_api = AnalyticsContentDto.res_kafka
_res_total_views = AnalyticsContentDto.res_total_views
_res_content_recent_views = AnalyticsContentDto.res_content_recent_views
_res_content_graph_views = AnalyticsContentDto.res_content_graph_views


@api.route("api/v1.0/content/views")
class KafkaViews(Resource):
    @api.expect(_req_api)
    @api.marshal_with(_res_api)
    # @token_required
    def post(self):
        ip = request.remote_addr
        device = request.user_agent.platform
        data = request.json
        return producer_kafka(data, ip, device)


@api.route("api/v1.0/content/consume")
class KafkaViews(Resource):
    @api.marshal_with(_res_api)
    # @token_required
    def get(self):
        return kafka_consumer()


@api.route("api/v1.0/brand/<brand_id>/totalviews")
class TotalViews(Resource):
    @api.marshal_with(_res_total_views)
    # @token_required
    def get(self, brand_id):
        args = request.args
        interval = args.get('interval')
        return total_views_content(brand_id, interval)


@api.route("api/v1.0/brand/<brand_id>/page/analytics")
class TotalViewsPage(Resource):
    @api.marshal_with(_res_content_recent_views)
    # @token_required
    def get(self, brand_id):
        args = request.args
        interval = args.get('interval')
        page = int(args.get('page', cur_app.config['PAGE']))
        limit = int(args.get('limit', cur_app.config['LIMIT']))
        return recent_published_content_pages(brand_id, interval, page, limit)


@api.route("api/v1.0/brand/<brand_id>/story/analytics")
class TotalViewsStory(Resource):
    @api.marshal_with(_res_content_recent_views)
    # @token_required
    def get(self, brand_id):
        args = request.args
        interval = args.get('interval')
        page = int(args.get('page', cur_app.config['PAGE']))
        limit = int(args.get('limit', cur_app.config['LIMIT']))
        return recent_published_content_storys(brand_id, interval, page, limit)


@api.route("api/v1.0/brand/<brand_id>/graph/analytics")
class TotalViewsStory(Resource):
    @api.marshal_with(_res_content_graph_views)
    # @token_required
    def get(self, brand_id):
        args = request.args
        interval = args.get('interval')
        return graph_analytics(brand_id, interval)
