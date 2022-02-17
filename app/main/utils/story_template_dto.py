from flask_restplus import Namespace, fields


class StoryTemplateDto:
    api = Namespace('story template',
                    description="Story Templated Related Opertation")

    request_template_story = api.model("request data", {
        'name': fields.String(required=True, description='String'),
        'raw_html': fields.String(required=True, description='String'),
        'block_count': fields.Integer(required=True, description='Int'),
        'block_structure': fields.List(fields.String, description='block_structure'),
        'thumbnail': fields.String(),
        'draft_css': fields.String(),
        'publish_css': fields.String(),
        'category': fields.String(),
        'social_support': fields.List(fields.String, description='social support')
    })
    response_template_story = api.model("response data", {
        'id': fields.String(required=True, description='UUID'),
        'name': fields.String(required=True, description='String'),
        'raw_html': fields.String(required=True, description='String'),
        'block_count': fields.Integer(required=True, description='Int'),
        'created_at': fields.String(required=True, description='int'),
        'update_at': fields.String(required=True, description='int'),
        'block_structure': fields.List(fields.String, description='block_structure'),
        'thumbnail': fields.String(),
        'draft_css': fields.String(),
        'publish_css': fields.String(),
        'category': fields.String(),
        'social_support': fields.List(fields.String, description='social support')
    })

    response_all_story_template = api.model("Get All templates", {
        "items": fields.List(fields.Nested(response_template_story)),
        "total_pages": fields.List(fields.Integer),
        "pages": fields.Integer(),
        "has_next": fields.Boolean(),
        "has_prev": fields.Boolean(),
        "page": fields.Integer(),
        "per_page": fields.Integer(),
        "total": fields.Integer()
    })
