from app.main.tokenvalidation.token_check import token_required
from flask import request
from flask_restplus import Resource

from app.main.services.widget_service import delete_faq_widget, delete_pricing_widget, delete_widget_tag, get_all_faq_widgets, get_all_pricing_widgets, get_all_widget_tag, get_faq_widget, get_pricing_widget, remove_widget_tag, save_faq_widget, save_pricing_widget, save_widget, get_all_widgets, delete_widget, save_widget_tag, update_faq_widget, update_pricing_widget, update_widget, get_widget, update_widget_tag
from app.main.utils.widget_dto import WidgetDTO

api = WidgetDTO.api
_req_post_widget = WidgetDTO.req_post_widget
_req_put_widget_with_id = WidgetDTO.req_put_widget_with_id
_res_post_widget = WidgetDTO.res_post_widget
_res_get_all_widgets = WidgetDTO.res_get_all_widgets

_req_post_pricing_widget = WidgetDTO.req_post_pricing_widget
_req_put_pricing_widget = WidgetDTO.req_put_pricing_widget
_res_post_pricing_widget = WidgetDTO.res_post_pricing_widget
_res_get_all_pricing_widgets = WidgetDTO.res_get_all_pricing_widgets

_req_post_faq_widget = WidgetDTO.req_post_faq_widget
_req_put_faq_widget = WidgetDTO.req_put_faq_widget
_res_post_faq_widget = WidgetDTO.res_post_faq_widget
_res_get_all_faq_widgets = WidgetDTO.res_get_all_faq_widgets

_req_post_widget_tag = WidgetDTO.req_post_widget_tag
_res_post_widget_tag = WidgetDTO.res_post_widget_tag
_res_all_widget_tag = WidgetDTO.all_widget_tag


@api.route("api/v1.0/widget")
class Widget(Resource):
    @api.expect(_req_post_widget)
    @api.marshal_with(_res_post_widget)
    def post(self):
        return save_widget(request.json)

    @api.marshal_with(_res_get_all_widgets)
    def get(self):
        args = request.args
        size = args.get('size')
        category = args.get('category')
        return get_all_widgets(size, category)


@api.route("api/v1.0/widget/<id>")
class WidgetNameOP(Resource):
    def delete(self, id):
        return delete_widget(id)

    @api.expect(_req_put_widget_with_id)
    @api.marshal_with(_res_post_widget)
    def put(self, id):
        return update_widget(id=id, data=request.json)

    @api.marshal_with(_res_post_widget)
    def get(self, id):
        return get_widget(id)


@api.route("api/v1.0/pricing/widget")
class PricingWidget(Resource):
    @api.expect(_req_post_pricing_widget)
    @api.marshal_with(_res_post_pricing_widget)
    def post(self):
        return save_pricing_widget(request.json)

    @api.marshal_with(_res_get_all_pricing_widgets)
    def get(self):
        return get_all_pricing_widgets()


@api.route("api/v1.0/pricing/widget/<id>")
class PricingWidgetID(Resource):
    def delete(self, id):
        return delete_pricing_widget(id)

    @api.expect(_req_put_pricing_widget)
    @api.marshal_with(_res_post_pricing_widget)
    def put(self, id):
        return update_pricing_widget(id=id, data=request.json)

    @api.marshal_with(_res_post_pricing_widget)
    def get(self, id):
        return get_pricing_widget(id)


@api.route("api/v1.0/faq/widget")
class FaqWidget(Resource):
    @api.expect(_req_post_faq_widget)
    @api.marshal_with(_res_post_faq_widget)
    def post(self):
        return save_faq_widget(request.json)

    @api.marshal_with(_res_get_all_faq_widgets)
    def get(self):
        return get_all_faq_widgets()


@api.route("api/v1.0/faq/widget/<id>")
class FaqWidgetID(Resource):
    def delete(self, id):
        return delete_faq_widget(id)

    @api.expect(_req_put_faq_widget)
    @api.marshal_with(_res_post_faq_widget)
    def put(self, id):
        return update_faq_widget(id=id, data=request.json)

    @api.marshal_with(_res_post_faq_widget)
    def get(self, id):
        return get_faq_widget(id)


@api.route("api/v1.0/widget/tag")
class WidgetTag(Resource):
    @api.expect(_req_post_widget_tag)
    @api.marshal_with(_res_post_widget_tag)
    def post(self):
        return save_widget_tag(request.json)

    @api.marshal_with(_res_all_widget_tag)
    def get(self):
        return get_all_widget_tag()


@api.route("api/v1.0/widget/tag/<tag_id>")
class WidgetTags(Resource):
    @api.expect(_req_post_widget_tag)
    @api.marshal_with(_res_post_widget_tag)
    def put(self, tag_id):
        return update_widget_tag(tag_id=tag_id, data=request.json)

    def delete(self, tag_id):
        return delete_widget_tag(tag_id)


@api.route("api/v1.0/widget/<widget_id>/tag/<tag_id>")
class WidgetTagsRemove(Resource):
    def delete(self, widget_id, tag_id):
        return remove_widget_tag(widget_id, tag_id)
