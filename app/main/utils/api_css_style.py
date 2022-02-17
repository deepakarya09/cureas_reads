from flask_restplus import Namespace, fields


class CssStyleAPI:
    api = Namespace("CssStyle", description="Css Style API")
    get_response_for_css_style = api.model("response for get api", {
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

    post_for_css_style = api.model("post for css style api", {
        "description": fields.String(required=True),
        "name": fields.String(required=True),
        "template_css_name": fields.String(required=True),
        "class_names": fields.List(fields.String, required=True),
        "active": fields.Boolean(required=True),
        "mobile_thumbnail": fields.String(required=False),
        "desktop_thumbnail": fields.String(required=False),
        "css_link": fields.String(required=True)
    })
    put_for_css_style = api.model("put for css style api", {
        "description": fields.String(required=False),
        "name": fields.String(required=False),
        "template_css_name": fields.String(required=False),
        "class_names": fields.List(fields.String, required=False),
        "active": fields.Boolean(required=False),
        "mobile_thumbnail": fields.String(required=False),
        "desktop_thumbnail": fields.String(required=False),
        "css_link": fields.String(required=False)
    })
    get_all_css_style = api.model("response all for get api", {
        "items": fields.List(fields.Nested(get_response_for_css_style)),
    })

    get_all_css_style_by_template_css_name = api.model("response all for get api by name", {
        "items": fields.List(fields.Nested(get_response_for_css_style)),
        "name": fields.String(),
        "widget_count": fields.Integer()
    })

    delete_response = api.model("delete for css style api", {
        "message": fields.String(required=False)
    })
