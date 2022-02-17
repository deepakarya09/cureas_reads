from app.main.tokenvalidation.token_check import scope, token_required
from flask import current_app as cur_app
import json

from flask import request, jsonify
from flask_restplus import Resource, abort
from flask_restplus._http import HTTPStatus

from app.main.controllers import error_m
from app.main.field_valiadators.api.brand_field_validations import PostBrandFieldValidator, PostBrandStyleFieldValidator
from app.main.services.brand_service import change_role_of_brand_user, get_all_brands, get_users_from_brand, post_brand, get_brand_details, post_brand_style, get_brand_from_user, \
    google_font, remove_user_from_brand, set_brand_active, update_brand
from app.main.utils.brand_dto import BrandingDto

api = BrandingDto.api
_req_brand = BrandingDto.req_brand
_req_style = BrandingDto.req_style
_res_style = BrandingDto.res_style
_get_all_brand_data = BrandingDto.get_all_brand_data
_res_brand = BrandingDto.res_brand
_get_all_brands_of_user = BrandingDto.get_all_brands_of_user
_get_brands = BrandingDto.get_all_brands
_get_all_users_of_brand = BrandingDto.get_all_users_of_brand
_response_message = BrandingDto.response_message

brand_validate = PostBrandFieldValidator()
style_validate = PostBrandStyleFieldValidator()


@api.route("api/v1.0/brand")
class BrandPost(Resource):
    @api.expect(_req_brand)
    @api.marshal_with(_res_brand)
    @token_required
    def post(self):
        data = request.json
        error = brand_validate.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return post_brand(data)


@api.route("api/v1.0/brand/<brand_id>")
class GetBrand(Resource):
    @api.marshal_with(_get_all_brand_data)
    @token_required
    def get(self, brand_id):
        return get_brand_details(brand_id=brand_id)


@api.route("api/v1.0/brand/update/<brand_id>")
class UpdateBrand(Resource):
    @api.marshal_with(_get_all_brand_data)
    @token_required
    def put(self, brand_id):
        data = request.json
        return update_brand(brand_id=brand_id, data=data)


@api.route("api/v1.0/style/<brand_id>")
class BrandStyle(Resource):
    @api.expect(_req_style)
    @api.marshal_with(_res_style)
    @token_required
    def post(self, brand_id):
        data = request.json

        error = style_validate.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return post_brand_style(brand_id=brand_id, data=data)


@api.route("api/v1.0/brands/<user_id>")
class Get_Brand(Resource):
    @api.marshal_with(_get_all_brands_of_user)
    @token_required
    def get(self, user_id):
        return get_brand_from_user(user_id)


@api.route("api/v1.0/users/brand/<brand_id>")
class Get_Brand(Resource):
    @api.marshal_with(_get_all_users_of_brand)
    @token_required
    def get(self, brand_id):
        return get_users_from_brand(brand_id)


@api.route("api/v1.0/brands")
class Get_Brand(Resource):
    @api.marshal_with(_get_brands)
    def get(self):
        args = request.args
        page = int(args.get('page', cur_app.config['PAGE']))
        limit = int(args.get('limit', cur_app.config['LIMIT']))
        searchKey = args.get('searchKey')
        category = args.get('category')
        return get_all_brands(page, limit, searchKey, category)


@api.route("api/v1.0/fonts")
class GetGoogleFonts(Resource):
    def get(self):
        return google_font()


@api.route("api/v1.0/brand/<brand_id>/setactive")
class ActiveBrand(Resource):
    @api.marshal_with(_get_all_brand_data)
    @token_required
    def get(self, brand_id):
        return set_brand_active(brand_id=brand_id)


@api.route("api/v1.0/brand/<brand_id>/user/<user_id>/remove")
class RemoveBrandUser(Resource):
    @api.marshal_with(_response_message)
    @token_required
    def delete(self, brand_id, user_id):
        return remove_user_from_brand(brand_id=brand_id, user_id=user_id)


@api.route("api/v1.0/brand/<brand_id>/user/<user_id>/role/<role_id>/change")
class RemoveBrandUser(Resource):
    @api.marshal_with(_response_message)
    @token_required
    def put(self, brand_id, user_id, role_id):
        return change_role_of_brand_user(brand_id=brand_id, user_id=user_id, role_id=role_id)
