from flask_restplus import Namespace, fields


class TemplateCssStyleAPI:
    api = Namespace("TemplateCssStyle", description="template css style API")
    get_response_for_template_css = api.model("response for get api", {
        "id": fields.String(),
        "description": fields.String(required=True),
        "widget_count": fields.Integer(required=True),
        "name": fields.String(),
        "created_at": fields.String(),
        "updated_at": fields.String()
    })
    response_for_css_style = api.model("response for get api", {
        "id": fields.String(),
        "description": fields.String(),
        "template_css_id": fields.String(),
        "class_names": fields.List(fields.String, required=True),
        "name": fields.String(),
        "active": fields.Boolean(),
        "created_at": fields.String(),
        "updated_at": fields.String(),
        "mobile_thumbnail": fields.String(),
        "desktop_thumbnail": fields.String(),
        "css_link": fields.String()
    })
    get_response_for_template_css_fetch = api.model("response for get api fetch", {
        "id": fields.String(),
        "description": fields.String(required=True),
        "widget_count": fields.Integer(required=True),
        "name": fields.String(),
        "created_at": fields.String(),
        "updated_at": fields.String(),
        "css_styles": fields.List(fields.Nested(response_for_css_style))
    })

    post_for_template_css = api.model("post for template css api", {
        "description": fields.String(required=False),
        "widget_count": fields.Integer(required=True),
        "name": fields.String(required=True)
    })
    put_for_template_css = api.model("put for template css api", {
        "description": fields.String(required=False),
        "widget_count": fields.Integer(required=False),
        "name": fields.String(required=False)
    })
    get_all_template_css = api.model("response all for get api", {
        "items": fields.List(fields.Nested(get_response_for_template_css_fetch)),
    })

    delete_response = api.model("delete for template css api", {
        "message": fields.String(required=False)
    })
