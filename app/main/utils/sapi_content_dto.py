from flask_restplus import Namespace, fields


class contentDto:
    api = Namespace("sapi content", description="Content API")

    res_name = api.model('tag post request', {
        'name': fields.String(required=True, description='tag')
    })

    res_content = api.model("Content", {
        "id": fields.String(description='uuid'),
        "title": fields.String(description='Content title'),
        "description": fields.String(description='Content description'),
        "site_link": fields.String(description='Content site_link'),
        "canonical_link": fields.String(description='Content canonical_link'),
        "image_link": fields.String(description='Content image_link'),
        "cdn_image_link": fields.String(description='Content image_link'),
        "source_id": fields.String(description='Content source uuid'),
        "type": fields.String(description='Content type'),
        "status": fields.String(description='Content city'),
        "country": fields.String(description='Content country'),
        "tags": fields.List(fields.Nested(res_name), attribute="con_conn", description="list of tags"),
        "content_type_id": fields.String(description='Content content_type'),
        "site_name": fields.String(description='Content site_name'),
        "created_at": fields.Integer(description="Unix timestamp"),
        "updated_at": fields.Integer(description="Unix timestamp")
    })

    res_all_content = api.model('response of all sources', {
        'items': fields.List(fields.Nested(res_content)),
        "totalPages": fields.List(fields.Integer),
        "page": fields.Integer(fields.Integer),
        "per_page": fields.Integer(fields.Integer),
        "total": fields.Integer(fields.Integer)

    })

    req_content = api.model('request of content', {
        "id": fields.String(description='uuid'),
        "title": fields.String(description='Content title'),
        "description": fields.String(description='Content description'),
        "site_link": fields.String(description='Content site_link'),
        "canonical_link": fields.String(description='Content canonical_link'),
        "image_link": fields.String(description='Content image_link'),
        "source_id": fields.String(description='Content source uuid'),
        "type": fields.String(description='Content type'),
        "country": fields.String(description='Content country'),
        "tags": fields.List(fields.String, description="list of tags"),
        "content_type_id": fields.String(description='Content content_type'),
        "site_name": fields.String(description='site_name'),
    })
    req_all_content = api.model('request of all sources', {})
