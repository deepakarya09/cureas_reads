from flask_restplus import Resource
from flask import request
from werkzeug.exceptions import abort
from app.main.controllers import error_m
from app.main.services.brand_social_accounts_services import add_user_to_social_access, create_social_account_instagram, create_social_account_linkedin, get_all_added_users, get_all_social_accounts, get_all_users_to_add, get_social_account, remove_social_account, remove_user_from_social_access, update_social_account
from app.main.tokenvalidation.token_check import token_required
from app.main.utils.api_brand_social_account_dto import SocialAccountsDto
from http import HTTPStatus

api = SocialAccountsDto.api

_res_all_api = SocialAccountsDto.res_all_social_accounts
_res_api = SocialAccountsDto.social_account
_req_for_update = SocialAccountsDto.req_for_update
_res_ig_post = SocialAccountsDto.insta_post_res
_res_li_post = SocialAccountsDto.linkedin_post_res
_req_post = SocialAccountsDto.req_post_social_account_instagram
_req_user_id = SocialAccountsDto.req_user_id
_res_message = SocialAccountsDto.res_message
_get_all_users = SocialAccountsDto.get_all_users


@api.route("api/v1.0/brand/<brand_id>/social")
class SocialAccountsAPI(Resource):
    @api.marshal_with(_res_all_api)
    # @token_required
    def get(self, brand_id):
        args = request.args
        name = args.get('name')
        return get_all_social_accounts(brand_id, name)


@api.route("api/v1.0/brand/<brand_id>/social/Instagram")
class SocialAccountInstagramAPI(Resource):
    @api.expect(_req_post)
    @api.marshal_with(_res_ig_post)
    @token_required
    def post(self, brand_id):
        data = request.json
        return create_social_account_instagram(brand_id, data)


@api.route("api/v1.0/brand/<brand_id>/social/Linkedin")
class SocialAccountLinkedinAPI(Resource):
    @api.expect(_req_post)
    @api.marshal_with(_res_li_post)
    @token_required
    def post(self, brand_id):
        data = request.json
        return create_social_account_linkedin(brand_id, data)


@api.route("api/v1.0/brand/<brand_id>/social/<social_id>/users_to_add")
class SocialAccountAccessUsersAPI(Resource):
    @api.marshal_with(_get_all_users)
    # @token_required
    def get(self, brand_id, social_id):
        return get_all_users_to_add(brand_id=brand_id, social_id=social_id)


@api.route("api/v1.0/brand/<brand_id>/social/<social_id>/users_added")
class SocialAccountAccessAddedUsersAPI(Resource):
    @api.marshal_with(_get_all_users)
    # @token_required
    def get(self, brand_id, social_id):
        return get_all_added_users(brand_id, social_id)


@api.route("api/v1.0/brand/<brand_id>/social/<social_id>/access")
class SocialAccountAccessAPI(Resource):

    @api.expect(_req_user_id)
    @api.marshal_with(_res_message)
    @token_required
    def post(self, brand_id, social_id):
        data = request.json
        return add_user_to_social_access(brand_id=brand_id, social_id=social_id, data=data)

    @api.expect(_req_user_id)
    @api.marshal_with(_res_message)
    @token_required
    def delete(self, brand_id, social_id):
        data = request.json
        return remove_user_from_social_access(brand_id=brand_id, social_id=social_id, data=data)


@api.route("api/v1.0/social/<social_id>")
class SocialAccountAPI(Resource):
    @api.expect(_req_for_update)
    @api.marshal_with(_res_api)
    @token_required
    def put(self, social_id):
        data = request.json
        return update_social_account(social_id=social_id, data=data)

    @api.marshal_with(_res_api)
    # @token_required
    def get(self, social_id):
        return get_social_account(social_id=social_id)

    @api.marshal_with(_res_message)
    @token_required
    def delete(self, social_id):
        return remove_social_account(social_id=social_id)
