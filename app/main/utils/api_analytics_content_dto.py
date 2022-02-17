from flask_restplus import Namespace, fields


class AnalyticsContentDto:
    api = Namespace("analytics_content", description="Brand Analytics Content")

    req_kafka = api.model("content vies", {
        "link": fields.String(),
        "content_id": fields.String()
    })

    res_kafka = api.model('response kafka', {
        "message": fields.String()
    })

    res_total_views = api.model('response total views', {
        "total_views": fields.Integer(),
        "percentage": fields.Integer()
    })

    content_recent_views = api.model('response total  recent views', {
        "name": fields.String(),
        "link": fields.String(),
        "image": fields.String(),
        "published_at": fields.String(),
        "views": fields.Integer(),
        "percentage": fields.Integer()
    })

    res_content_recent_views = api.model('response recent page views', {
        'items': fields.List(fields.Nested(content_recent_views)),
        "total_pages": fields.List(fields.Integer),
        "pages": fields.Integer(),
        "has_next": fields.Boolean(),
        "has_prev": fields.Boolean(),
        "page": fields.Integer(),
        "per_page": fields.Integer(),
        "total": fields.Integer()
    })

    res_content_graph_views = api.model('response graph views', {
        'views_desktop': fields.List(fields.Integer),
        'views_mobile': fields.List(fields.Integer),
        "data": fields.List(fields.String)
    })
