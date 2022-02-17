from flask_restplus import Resource
from flask import current_app as cur_app
from flask import request
from app.main.services.story.story_sharing_services import all_sharing_logs, get_available_platform, list_of_social_accounts, posting_story, sharing_log_marketing, sharing_story
from app.main.utils.api_story_sharing_dto import StorySharingDTO
from app.main.tokenvalidation.token_check import token_required
api = StorySharingDTO.api
_res_social_available = StorySharingDTO.allowed_social_response
_res_social_account = StorySharingDTO.list_social_account
_req_for_share = StorySharingDTO.req_for_sharing
_res_for_share = StorySharingDTO.res_for_sharing
_response_share = StorySharingDTO.response_share
_res_sharing_logs = StorySharingDTO.res_sharing_logs
_res_sharing_logs_marketing = StorySharingDTO.res_sharing_logs_marketing


@api.route("api/v1.0/brand/<brand_id>/template/<template_id>/sharing")
class StorySharingAPI(Resource):
    @api.marshal_with(_res_social_available)
    @token_required
    def get(self, brand_id, template_id):
        return get_available_platform(brand_id, template_id)


@api.route("api/v1.0/brand/<brand_id>/sharing")
class StorySharingsAPI(Resource):
    @api.marshal_with(_res_social_account)
    @token_required
    def get(self, brand_id):
        args = request.args
        name = args.get('name')
        return list_of_social_accounts(brand_id, name)


@api.route("api/v1.0/brand/<brand_id>/story/<story_id>/share")
class StoryShareAPI(Resource):
    @api.expect(_req_for_share)
    @api.marshal_with(_res_for_share)
    @token_required
    def post(self, brand_id, story_id):
        return sharing_story(brand_id, story_id, data=request.json)


@api.route("api/v1.0/share/<log_id>")
class StoryShareLogAPI(Resource):
    @api.marshal_with(_response_share)
    # @token_required
    def get(self, log_id):
        return posting_story(log_id)


@api.route("api/v1.0/share/log")
class StoryShareLogAPI(Resource):
    @api.marshal_with(_res_sharing_logs)
    # @token_required
    def get(self):
        args = request.args
        success = args.get('success')
        story_id = args.get('story_id')
        social_id = args.get('social_id')
        user_id = args.get('user_id')
        page = int(args.get('page', cur_app.config['PAGE']))
        limit = int(args.get('limit', cur_app.config['LIMIT']))
        return all_sharing_logs(success, story_id, social_id, user_id, page, limit)


@api.route("api/v1.0/brand/<brand_id>/sharelog")
class StoryShareLogAPI(Resource):
    @api.marshal_with(_res_sharing_logs_marketing)
    # @token_required
    def get(self, brand_id):
        args = request.args
        page = int(args.get('page', cur_app.config['PAGE']))
        limit = int(args.get('limit', cur_app.config['LIMIT']))
        search = args.get('search')
        return sharing_log_marketing(brand_id, page, limit, search)
