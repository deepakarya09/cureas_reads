from flask_restplus import Namespace, fields


class BradPageDTO:
    api = Namespace("Brand-User Page")

    parsed_data = api.model("Page Data", {
        "id": fields.String(),
        "block_no": fields.Integer(),
        "widget_name": fields.String(),
        "widget_page": fields.String(),
        "updated": fields.Boolean(default=False)
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
        "first_brand_exists": fields.Boolean()
    })

    res_issue_template = api.model("Response page data", {
        "id": fields.String(),
        "template_html": fields.String(),
        "page_data": fields.List(fields.Nested(parsed_data)),
        "parsed_html": fields.String(),
        'category': fields.String(),
    })

    res_page_by_id = api.model("Response page data", {
        "page_name": fields.String(),
        "raw_template": fields.String(),
        "template_id": fields.String(),
        "template_html": fields.String(),
        "page_data": fields.List(fields.Nested(parsed_data)),
        "category": fields.String(),
        "thumbnail_image": fields.String(),
        "active": fields.Boolean(),
        "editors": fields.List(cls_or_instance=fields.Nested(user_data))
    })

    parsed_data_before_save = api.model("Page Data", {
        "block_no": fields.Integer(),
        "widget_type": fields.String(),
        "widget_name": fields.String(),
        "widget_page": fields.String(),
        "updated": fields.Boolean(default=False)
    })

    res_issue_template_before_save = api.model("Response page data", {
        "raw_template": fields.String(),
        "template_html": fields.String(),
        "page_data": fields.List(fields.Nested(parsed_data_before_save)),
        "page_name": fields.String(),
    })

    parsed_data_draft_published = api.model("Page Data", {
        "block_no": fields.Integer(),
        "widget_name": fields.String(),
        "widget_type": fields.String(),
        "widget_page": fields.String(),
        "updated": fields.Boolean()

    })

    seo_data = api.model("SEO DATA", {
        "seo_title": fields.String(),
        "seo_description": fields.String(),
        "page_type": fields.String(),
        "banner_image": fields.String(),
        'twitter_id': fields.String(),
        "facebook_publisher": fields.String()
    })

    req_for_draft_publish = api.model("PUBLISH or DRAFT", {
        "template_id": fields.String(),
        "raw_template": fields.String(),
        "page_name": fields.String(),
        "page_data": fields.List(fields.Nested(parsed_data_draft_published)),
        "status": fields.String(),
        'category': fields.String(),
        "seo_data": fields.Nested(seo_data, required=False)
    })

    req_for_draft_publish_update = api.model("PUBLISH or DRAFT", {
        "template_id": fields.String(),
        "raw_template": fields.String(),
        "page_name": fields.String(),
        "page_data": fields.List(fields.Nested(parsed_data_draft_published)),
        "status": fields.String(),
        'category': fields.String()
    })

    res_for_draft_publish = api.model("PUBLISH or DRAFT response", {
        "id": fields.String(),
        "link": fields.String(),
        "template_id": fields.String(),
        "template_html": fields.String(),
        "thumbnail_image": fields.String(),
        "raw_template": fields.String(),
        "page_name": fields.String(),
        "page_data": fields.List(fields.Nested(parsed_data_draft_published)),
        "status": fields.String(),
        'category': fields.String(),
        "active": fields.Boolean(),
    })

    res_get_all_draft_and_publish = api.model("Get all for draft and publish", {
        "id": fields.String(),
        "brand_id": fields.String(),
        "updated_at": fields.String(),
        "page_name": fields.String(),
        "template_id": fields.String(),
        "total_block_count": fields.Integer(),
        "html": fields.String(),
        "thumbnail_image": fields.String(),
        "link": fields.String(),
        "filled_block_count": fields.Integer(),
        "status": fields.String(),
        'category': fields.String(),
        "active": fields.Boolean(),
        "editors": fields.List(cls_or_instance=fields.Nested(user_data))
    })
    res_get_all_system = api.model("Get all for system", {
        "id": fields.String(),
        "brand_id": fields.String(),
        "updated_at": fields.String(),
        "created_at": fields.String(),
        "page_name": fields.String(),
        "template_id": fields.String(),
        "total_block_count": fields.Integer(),
        "thumbnail_image": fields.String(),
        "filled_block_count": fields.Integer(),
        "status": fields.String(),
        'category': fields.String(),
        "active": fields.Boolean(),
        "page_data": fields.List(fields.Nested(parsed_data_draft_published)),
    })
    res_all_system_pages = api.model("Get all System pages", {
        "items": fields.List(fields.Nested(res_get_all_system)),
        "total_pages": fields.List(fields.Integer),
        "pages": fields.Integer(),
        "has_next": fields.Boolean(),
        "has_prev": fields.Boolean(),
        "page": fields.Integer(),
        "per_page": fields.Integer(),
        "total": fields.Integer()
    })
    res_all_draft_pub = api.model("Response all page", {
        "items": fields.List(fields.Nested(res_get_all_draft_and_publish)),
        "total_pages": fields.List(fields.Integer),
        "pages": fields.Integer(),
        "has_next": fields.Boolean(),
        "has_prev": fields.Boolean(),
        "page": fields.Integer(),
        "per_page": fields.Integer(),
        "total": fields.Integer()
    })
    response_html = api.model("html", {
        "data": fields.String(),

    })

    res_all_content = api.model('response of all PAGE', {
        "items": fields.List(fields.Nested(response_html)),
        "total_pages": fields.List(fields.Integer),
        "white_theme_logo": fields.String(),
        "black_theme_logo": fields.String(),
        "has_next": fields.Boolean(),
        "has_prev": fields.Boolean(),
        "page": fields.Integer(),
        "per_page": fields.Integer(),
        "total": fields.Integer()

    })

    res_for_preview_page = api.model("response for preview page", {
        "page_id": fields.String(),
        "category": fields.String(),
        "active": fields.Boolean(),
        "parsed_html_page": fields.String()
    })

    req_for_image_upload = api.model("request for image upload", {
        "image": fields.String(required=True),
    })
    res_for_image_upload = api.model("response for image upload", {
        "image_link": fields.String()
    })
