from flask_restplus import Namespace, fields


class WidgetDTO:
    api = Namespace("Widget", )
    wild = fields.Wildcard(fields.String)

    req_post_widget = api.model("Post Widget Request", {
        "name": fields.String(required=True),
        "raw_html": fields.String(required=True),
        "default_data": fields.String(required=True),
        'thumbnail': fields.String(),
        'category': fields.String(required=True),
        "type": fields.String(required=True),
        "tag": fields.String(required=False)
    })
    req_post_widget_tag = api.model("Post Widget Tag Request", {
        "name": fields.String(required=True)
    })
    res_post_widget_tag = api.model("Post Widget Tag Response", {
        "id": fields.String(),
        "name": fields.String()
    })
    all_widget_tag = api.model("All widget Tag", {
        "items": fields.List(fields.Nested(res_post_widget_tag))
    })

    res_post_widget = api.model("Post Widget Response", {
        "id": fields.String(),
        "name": fields.String(),
        "parsed_html": fields.String(attribute='html'),
        "created_at": fields.String(),
        "updated_at": fields.String(),
        'thumbnail': fields.String(),
        'category': fields.String(),
        "type": fields.String(),
        "tags": fields.List(fields.String)
    })

    req_put_widget_with_id = api.model("Update older widget", {
        "name": fields.String(),
        "raw_html": fields.String(),
        "default_data": fields.String(),
        'thumbnail': fields.String(),
        'category': fields.String(),
        "type": fields.String(),
        "tag": fields.String()
    })

    res_get_all_widgets = api.model("Get all widgets", {
        "items": fields.List(fields.Nested(res_post_widget))
    })

    buttons = api.model("Buttons", {
        "text": fields.String(),
        "link": fields.String()
    })

    req_post_pricing_widget = api.model("Post pricing Widget Request", {
        "title": fields.String(required=True),
        "subtitle": fields.String(required=True),
        "brand_id": fields.String(required=False),
        'point_1': fields.String(required=False),
        'point_2': fields.String(required=False),
        'point_3': fields.String(required=False),
        'point_4': fields.String(required=False),
        'point_5': fields.String(required=False),
        'point_6': fields.String(required=False),
        'point_7': fields.String(required=False),
        'point_8': fields.String(required=False),
        'point_9': fields.String(required=False),
        'point_10': fields.String(required=False),
        'button': fields.Nested(buttons, required=False)
    })

    req_put_pricing_widget = api.model("Update pricing Widget Request", {
        "title": fields.String(required=False),
        "subtitle": fields.String(required=False),
        "brand_id": fields.String(required=False),
        'point_1': fields.String(required=False),
        'point_2': fields.String(required=False),
        'point_3': fields.String(required=False),
        'point_4': fields.String(required=False),
        'point_5': fields.String(required=False),
        'point_6': fields.String(required=False),
        'point_7': fields.String(required=False),
        'point_8': fields.String(required=False),
        'point_9': fields.String(required=False),
        'point_10': fields.String(required=False),
        'button': fields.Nested(buttons, required=False)
    })

    res_post_pricing_widget = api.model("Response Pricing Widget Request", {
        "id": fields.String(required=True),
        "created_at": fields.String(required=True),
        "brand_id": fields.String(required=False),
        "title": fields.String(required=True),
        "subtitle": fields.String(required=True),
        "brand_id": fields.String(required=False),
        'point_1': fields.String(required=False),
        'point_2': fields.String(required=False),
        'point_3': fields.String(required=False),
        'point_4': fields.String(required=False),
        'point_5': fields.String(required=False),
        'point_6': fields.String(required=False),
        'point_7': fields.String(required=False),
        'point_8': fields.String(required=False),
        'point_9': fields.String(required=False),
        'point_10': fields.String(required=False),
        'button': fields.Nested(buttons, required=False)
    })

    res_get_all_pricing_widgets = api.model("Get all pricing widgets", {
        "items": fields.List(fields.Nested(req_post_pricing_widget))
    })
    faq = api.model("faq", {
        "title": fields.String(),
        "description": fields.String()
    })

    req_post_faq_widget = api.model("Post faq Widget Request", {
        "data": fields.Nested(faq),
        "brand_id": fields.String(required=False),
    })

    req_put_faq_widget = api.model("Update faq Widget Request", {
        "brand_id": fields.String(required=False),
        "data": fields.Nested(faq),
    })

    res_post_faq_widget = api.model("Response Pricing Widget Request", {
        "id": fields.String(required=True),
        "created_at": fields.String(required=True),
        "brand_id": fields.String(required=False),
        "data": fields.Nested(faq),
    })

    res_get_all_faq_widgets = api.model("Get all pricing widgets", {
        "items": fields.List(fields.Nested(res_post_faq_widget))
    })
