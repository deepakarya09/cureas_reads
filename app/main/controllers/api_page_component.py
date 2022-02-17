from flask_restplus import Resource
from app.main.services.pages.page_component_services import component_to_all_brand, delete_page_component, get_all_page_component, get_page_component, post_page_component, put_brand_page_component, update_page_component
from app.main.tokenvalidation.token_check import token_required
from app.main.utils.api_page_component import PageComponentAPI
from flask import request

api = PageComponentAPI.api

_get_all_page_component = PageComponentAPI.get_all_component_response
_response_for_brand_component = PageComponentAPI.response_for_saved_data
_post_data_for_brand = PageComponentAPI.post_data_for_brand
_post_page_componet = PageComponentAPI.post_page_component
_get_page_component = PageComponentAPI.get_page_component
_put_page_componet = PageComponentAPI.put_page_component_request


@api.route("api/v1.0/brand/<brand_id>/pagecomponent")
class AllComponentBrand(Resource):
    @api.marshal_with(_get_all_page_component)
    def get(self, brand_id):
        args = request.args
        category = args.get('category')
        return get_all_page_component(brand_id, category)

    @api.expect(_post_data_for_brand)
    @api.marshal_with(_response_for_brand_component)
    def put(self, brand_id):
        data = request.json
        args = request.args
        category = args.get('category')
        return put_brand_page_component(brand_id, category, data)


@api.route("api/v1.0/page/component")
class PageComponent(Resource):
    @api.expect(_post_page_componet)
    @api.marshal_with(_get_page_component)
    def post(self):
        data = request.json
        return post_page_component(data)


@api.route("api/v1.0/page/component/<component_id>")
class PageComponentID(Resource):
    @api.expect(_put_page_componet)
    @api.marshal_with(_get_page_component)
    def put(self, component_id):
        data = request.json
        return update_page_component(component_id, data)

    @api.marshal_with(_get_page_component)
    def get(self, component_id):
        return get_page_component(component_id)

    @api.marshal_with(_response_for_brand_component)
    def delete(self, component_id):
        return delete_page_component(component_id)


@api.route("api/v1.0/brand/script/add/component")
class ScriptAddBrandComponent(Resource):
    @api.marshal_with(_response_for_brand_component)
    def get(self):
        return component_to_all_brand()
