from flask_restplus import Namespace, fields


class BrandingDto:
    api = Namespace('Branding')

    color = api.model("Colors", {
        "primary": fields.String(),
        "secondary": fields.String()
    })

    fonts = api.model("Colors", {
        "main": fields.String(),
        "secondary": fields.String()
    })

    req_brand = api.model("Brand Info", {
        "brand_id": fields.String(),
        "name": fields.String(),
        "site_url": fields.Url(),
        "user_id": fields.String(),
        "description": fields.String(),
        "facebook_url": fields.String(default=None),
        "twitter_url": fields.String(),
        "instagram_url": fields.String()
    })

    res_brand = api.model("Brand Return Response", {
        "id": fields.String(),
        "user_id": fields.String(),
        "name": fields.String(),
        "site_url": fields.String(),
        "description": fields.String(),
        "facebook_url": fields.String(),
        "twitter_url": fields.String(),
        "instagram_url": fields.String(),
        "created_at": fields.String(),
        "updated_at": fields.String()
    })

    req_style = api.model("style req details", {
        "user_id": fields.String(required=True),
        "white_theme_logo": fields.String(),
        "black_theme_logo": fields.String(),
        "colors": fields.Nested(color),
        "fonts": fields.Nested(fonts),
        "light_theme": fields.Boolean(),
    })

    res_style = api.model("style res details", {
        "id": fields.String(),
        "user_id": fields.String(),
        "white_theme_logo": fields.String(),
        "black_theme_logo": fields.String(),
        "colors": fields.Nested(color),
        "fonts": fields.Nested(fonts),
        "light_theme": fields.Boolean(),
    })

    get_all_brand_data = api.model("Brand Details", {
        "id": fields.String(),
        "user_id": fields.String(),
        "user_role": fields.String(),
        "name": fields.String(),
        "site_url": fields.String(),
        "description": fields.String(),
        "facebook_url": fields.String(),
        "twitter_url": fields.String(),
        "instagram_url": fields.String(),
        "created_at": fields.String(),
        "updated_at": fields.String(),
        "white_theme_logo": fields.String(),
        "black_theme_logo": fields.String(),
        "colors": fields.Nested(color),
        "fonts": fields.Nested(fonts),
        "light_theme": fields.Boolean(),
        "seo_description": fields.String(),
        "seo_title": fields.String(),
        "favicon_img": fields.String(),
        "terms_condition": fields.String(),
        "privacy_policy": fields.String(),
        "font_size": fields.Integer(),
        "active": fields.Boolean(),
        "email_api_key": fields.String()

    })
    page_data = api.model("values", {
        "id": fields.String(description='uuid'),
        "cdn_html_page_link": fields.String(description='link'),
        "status": fields.String(description='status'),

    })

    brand_data_first_page = api.model("Brand Data link", {
        "id": fields.String(),
        "name": fields.String(),
        "fqdn": fields.String(),
        "branding_page": fields.List(fields.Nested(page_data), attribute="branding_page", )
    })

    get_all_brands = api.model("get all brands", {
        "items": fields.List(fields.Nested(brand_data_first_page)),
        "total_pages": fields.List(fields.Integer),
        "has_next": fields.Boolean(),
        "has_prev": fields.Boolean(),
        "page": fields.Integer(),
        "per_page": fields.Integer(),
        "total": fields.Integer()
    })

    brand_role = api.model(" users role of brand", {
        "id": fields.String(),
        "role": fields.String()
    })
    user_data = api.model("user Data", {
        "id": fields.String(),
        "first_name": fields.String(),
        "last_name": fields.String(),
        "email": fields.String(),
        "image_url": fields.String(),
        "role": fields.String(),
        "verified": fields.Boolean(description='Verification of user'),
        "login_type": fields.String(attribute="login_type"),
        "first_brand_exists": fields.Boolean(),
        "brand_role": fields.List(cls_or_instance=fields.Nested(brand_role))

    })

    get_all_users_of_brand = api.model("all users of brand", {
        "items": fields.List(cls_or_instance=fields.Nested(user_data))
    })

    get_all_brands_of_user = api.model("all brands of user", {
        "items": fields.List(cls_or_instance=fields.Nested(get_all_brand_data))
    })

    response_message = api.model("response message", {
        "message": fields.String(attribute="message")
    })
