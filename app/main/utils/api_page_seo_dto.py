from flask_restplus import Namespace, fields


class BrandPageSeoDto:
    api = Namespace('Brand_page_seo')

    seo_request = api.model("Seo Request", {
        "title": fields.String(required=False),
        "icon": fields.String(required=False),
        "description": fields.String(required=False),
        "page_type": fields.String(required=False),
        "facebook_publisher": fields.String(required=False),
        "banner_image": fields.String(required=False),
        "twitter_id": fields.String(required=False)
    })

    seo_response = api.model("Seo Response", {
        "id": fields.String(),
        "page_id": fields.String(),
        "icon": fields.String(),
        "title": fields.String(),
        "description": fields.String(),
        "page_link": fields.String(),
        "page_type": fields.String(),
        "facebook_publisher": fields.String(),
        "banner_image": fields.String(),
        "twitter_id": fields.String(),
        "created_at": fields.String(),
        "updated_at": fields.String()
    })
