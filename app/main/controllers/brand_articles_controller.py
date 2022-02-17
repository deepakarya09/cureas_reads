from app.main.tokenvalidation.token_check import token_required
from app.main.services.brand_articles_service import delete_article, get_all_articles, get_article, update_article, validations
from flask_restplus import Resource
from app.main.utils.brand_articles_dto import BrandArticleDTO
from flask import request
from app.main.field_valiadators.api.api_brand_article_validator import apiBrandArticleValidator
from werkzeug.exceptions import abort
from http import HTTPStatus
from app.main.controllers import error_m
from flask import current_app as cur_app

api = BrandArticleDTO.api
_req_article = BrandArticleDTO.req_post_article
_res_article = BrandArticleDTO.res_post_article
_res_all = BrandArticleDTO.res_get_all_request

_article_validator = apiBrandArticleValidator()


@api.route("api/v1.0/brand/<brand_id>/article")
class Article(Resource):
    @api.expect(_req_article)
    @api.marshal_with(_res_article)
    @token_required
    def post(self, brand_id):
        data = request.json
        error = _article_validator.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return validations(data, brand_id=brand_id)


@api.route("api/v1.0/brand/<brand_id>/articles")
class GetArticleAll(Resource):
    @api.marshal_with(_res_all)
    def get(self, brand_id):
        args = request.args
        page = int(args.get('page', cur_app.config['PAGE']))
        limit = int(args.get('limit', cur_app.config['LIMIT']))
        searchKey = args.get('searchKey')
        return get_all_articles(brand_id, searchKey, page, limit)


@api.route("api/v1.0/brand/<brand_id>/article/<article_id>")
class GetArticle(Resource):
    @api.marshal_with(_res_article)
    @token_required
    def get(self, article_id):
        return get_article(article_id)

    def delete(self, article_id):
        return delete_article(article_id)

    @api.expect(_req_article)
    @api.marshal_with(_res_article)
    @token_required
    def put(self,brand_id, article_id):
        data = request.json
        error = _article_validator.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return update_article(data, article_id=article_id,brand_id=brand_id)
