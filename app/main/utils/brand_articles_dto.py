from flask_restplus import Namespace, fields


class BrandArticleDTO:
    api = Namespace("User Articles for Branding")

    req_post_article = api.model("Article Post Request", {
        "title": fields.String(required=True),
        "description": fields.String(required=True),
        "canonical_link": fields.String(required=True),
        "image_link": fields.String(required=True),
        "content_type": fields.String(required=True),
        "tags": fields.List(fields.String, required=True, description='Tags'),
        "site_name": fields.String(required=True),
        "favicon_icon_link": fields.String(required=True),
    })

    res_post_article = api.model("Article Post Request", {
        "id": fields.String(),
        "user_id": fields.String(),
        "brand_id": fields.String(),
        "title": fields.String(),
        "description": fields.String(),
        "canonical_link": fields.String(),
        "image_link": fields.String(),
        "favicon_icon_link": fields.String(),
        "content_type": fields.String(),
        "tags": fields.List(fields.String, required=True, description='Tags'),
        "site_name": fields.String(),
        "created_at": fields.String(),
        "updated_at": fields.String()
    })

    res_get_all_request = api.model("Get All User articles", {
        "items": fields.List(fields.Nested(res_post_article)),
        "total_pages": fields.List(fields.Integer),
        "has_next": fields.Boolean(),
        "has_prev": fields.Boolean(),
        "page": fields.Integer(),
        "per_page": fields.Integer(),
        "total": fields.Integer()
    })
