from flask_restplus import Namespace, fields


class SourceDto:
    api = Namespace("source", description="source related operations")
    req_source = api.model("request source", {
        "name": fields.String(required=True, description='source name'),
        "website_link": fields.String(required=True, description='website link'),
        "stream_link": fields.String(required=True, description='stream/rss link'),
        "stream_type": fields.String(required=True, description='stream type'),
        "content_type": fields.List(fields.String, description="list of uuid of content type"),
        "polling_interval": fields.Integer(required=True, description='polling interval in minutes'),
        "region": fields.List(fields.String, description="list of regions"),
    })

    req_all_resources = api.model("req all sources", {})

    res_source = api.model("response source", {
        "id": fields.String(description='uuid'),
        "name": fields.String(description='source name'),
        "website_link": fields.String(description='website link'),
        "stream_link": fields.String(description='stream/rss link'),
        "stream_type": fields.String(description='stream type'),
        "content_type": fields.List(fields.String),
        "polling_interval": fields.Integer(description='polling interval in minutes'),
        "region": fields.List(fields.String, description="list of regions"),
        "created_at": fields.Integer(description='data inserted at'),
        "updated_at": fields.Integer(description='last update')
    })

    res_sources = api.model('response of all sources', {
        'items': fields.List(fields.Nested(res_source),attribute="items",),
        "page": fields.Integer(fields.Integer),
        "per_page": fields.Integer(fields.Integer),
        "total": fields.Integer(fields.Integer),
        "totalPages": fields.List(fields.Integer,attribute="total_pages",)

    })

    req_for_put = api.model("update content", {
        "id": fields.String(description='uuid'),
        "name": fields.String(description='source name'),
        "website_link": fields.String(description='website link'),
        "stream_link": fields.String(description='stream/rss link'),
        "stream_type": fields.String(description='stream type'),
        "content_type": fields.List(fields.String),
        "polling_interval": fields.Integer(description='polling interval in minutes'),
        "region": fields.List(fields.String, description="list of regions"),
    })
