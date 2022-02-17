from flask_restplus import Namespace, fields


class api_contentDto:
    api = Namespace("api_content", description="Content API")
    res_id = api.model('tag post request', {
        'id': fields.String(required=True, description='tag')
    })

    res_api_content = api.model("Content", {
        "id": fields.String(description='uuid'),
        "title": fields.String(description='content title'),
        "description": fields.String(description='content description'),
        "site_link": fields.String(description='content site_link'),
        "canonical_link": fields.String(description='content canonical_link'),
        "image_link": fields.String(description='content image_link'),
        "source_id": fields.String(description='content source uuid'),
        "type": fields.String(description='content type'),
        "status": fields.String(description='Content city'),
        "country": fields.String(description='content country'),
        "tag_ids": fields.List(fields.Nested(res_id), attribute="con_conn", description="list of tags"),
        "content_type": fields.String(description='content_type'),
        "site_name": fields.String(description='content site_name'),
        "created_at": fields.Integer(description="Unix timestamp"),
        "updated_at": fields.Integer(description="Unix timestamp")
    })

    res_all_api_content = api.model('response of all sources', {
        'items': fields.List(fields.Nested(res_api_content)),
        "totalPages": fields.List(fields.Integer),
        "page": fields.Integer(fields.Integer),
        "per_page": fields.Integer(fields.Integer),
        "total": fields.Integer(fields.Integer)
    })

    req_api_content = api.model('request of content', {
        "title": fields.String(description='content title'),
        "description": fields.String(description='content description'),
        "site_link": fields.String(description='content site_link'),
        "canonical_link": fields.String(description='content canonical_link'),
        "image_link": fields.String(description='content image_link'),
        "source_id": fields.String(description='content source uuid'),
        "type": fields.String(description='content type'),
        "country": fields.String(description='content country'),
        "tag_ids": fields.List(fields.String, description="list of tags"),
        "content_type": fields.String(description='content_type'),
        "site_name": fields.String(description='content site_name'),

    })

    req_all_api_content = api.model('request of all sources', {})
