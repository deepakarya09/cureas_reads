from flask_restplus import Namespace, fields


class BrandStoryDTO:
    api = Namespace("Brand-Story")

    parsed_data = api.model("Story Data", {
        "block_no": fields.Integer(),
        "widget_type": fields.String(),
        "widget_name": fields.String(),
        "widget_page": fields.String(),
        "updated": fields.Boolean(default=False)
    })

    seo_data = api.model("SEO DATA", {
        "seo_title": fields.String(),
        "seo_description": fields.String(),
        "story_type": fields.String(),
        "banner_image": fields.String(),
        'twitter_id': fields.String(),
        "facebook_publisher": fields.String()
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

    res_story_by_id = api.model("Response story data", {
        "story_name": fields.String(),
        "raw_template": fields.String(),
        "template_id": fields.String(),
        "template_html": fields.String(),
        "story_data": fields.List(fields.Nested(parsed_data)),
        "category": fields.String(),
        "thumbnail_image": fields.String(),
        "active": fields.Boolean(),
        "editors": fields.List(cls_or_instance=fields.Nested(user_data))
    })

    res_issue_template_before_save = api.model("Response story blank data", {
        "raw_template": fields.String(),
        "template_html": fields.String(),
        "story_data": fields.List(fields.Nested(parsed_data)),
        "story_name": fields.String(),
    })

    post_req_for_draft_publish = api.model("PUBLISH or DRAFT", {
        "template_id": fields.String(),
        "raw_template": fields.String(),
        "story_name": fields.String(),
        "story_data": fields.List(fields.Nested(parsed_data)),
        "status": fields.String(),
        'category': fields.String(),
        "seo_data": fields.Nested(seo_data, required=False)
    })

    post_req_for_draft_publish_update = api.model("PUBLISH or DRAFT update", {
        "template_id": fields.String(),
        "raw_template": fields.String(),
        "story_name": fields.String(),
        "story_data": fields.List(fields.Nested(parsed_data)),
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
        "story_name": fields.String(),
        "story_data": fields.List(fields.Nested(parsed_data)),
        "status": fields.String(),
        'category': fields.String(),
        "active": fields.Boolean(),
    })

    res_get_all_draft_and_publish = api.model("Get all for draft and publish story", {
        "id": fields.String(),
        "brand_id": fields.String(),
        "updated_at": fields.String(),
        "story_name": fields.String(),
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
        "story_name": fields.String(),
        "template_id": fields.String(),
        "total_block_count": fields.Integer(),
        "thumbnail_image": fields.String(),
        "filled_block_count": fields.Integer(),
        "status": fields.String(),
        'category': fields.String(),
        "active": fields.Boolean(),
        "page_data": fields.List(fields.Nested(parsed_data)),
    })

    res_all_Storye_pages = api.model("Get all story pages", {
        "items": fields.List(fields.Nested(res_get_all_system)),
        "total_pages": fields.List(fields.Integer),
        "pages": fields.Integer(),
        "has_next": fields.Boolean(),
        "has_prev": fields.Boolean(),
        "page": fields.Integer(),
        "per_page": fields.Integer(),
        "total": fields.Integer()
    })

    res_get_all_draft_and_publish_story = api.model("Response all page", {
        "items": fields.List(fields.Nested(res_get_all_draft_and_publish)),
        "total_pages": fields.List(fields.Integer),
        "pages": fields.Integer(),
        "has_next": fields.Boolean(),
        "has_prev": fields.Boolean(),
        "page": fields.Integer(),
        "per_page": fields.Integer(),
        "total": fields.Integer()
    })
