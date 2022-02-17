from flask_restplus import Namespace, fields


class TemplateDto:
    api = Namespace('template', description="Templated Related Opertation")

    request_template = api.model("request data", {
        'name': fields.String(required=True, description='String'),
        'raw_html': fields.String(required=True, description='String'),
        'block_count': fields.Integer(required=True, description='Int'),
        'block_structure':fields.List(fields.String, description='block_structure'),
        'thumbnail': fields.String(),
        'draft_css':fields.String(),
        'publish_css':fields.String(),
        'category':fields.String(),
    })
    response_template = api.model("response data", {
        'id': fields.String(required=True, description='UUID'),
        'name': fields.String(required=True, description='String'),
        'raw_html': fields.String(required=True, description='String'),
        'block_count': fields.Integer(required=True, description='Int'),
        'created_at': fields.String(required=True, description='int'),
        'update_at': fields.String(required=True, description='int'),
        'block_structure':fields.List(fields.String, description='block_structure'),
        'thumbnail': fields.String(),
        'draft_css':fields.String(),
        'publish_css':fields.String(),
        'category':fields.String(),
    })

    response_all = api.model("Get All templates", {
        "items": fields.List(fields.Nested(response_template)),
        "total_pages": fields.List(fields.Integer),
        "pages": fields.Integer(),
        "has_next": fields.Boolean(),
        "has_prev": fields.Boolean(),
        "page": fields.Integer(),
        "per_page": fields.Integer(),
        "total": fields.Integer()
    })
