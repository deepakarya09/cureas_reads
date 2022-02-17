from marshmallow import Schema, fields
from marshmallow.validate import Length, OneOf


class StoryTemplateValidator(Schema):
    name = fields.String(required=False, validate=Length(min=1, max=50))
    draft_css = fields.URL(required=False, validate=Length(min=1, max=500))
    publish_css = fields.URL(required=False, validate=Length(min=1, max=500))
    raw_html = fields.String(required=False)
    thumbnail = fields.String(required=False)
    block_structure = fields.List(
        required=False, cls_or_instance=fields.String)
    block_count = fields.Integer(required=False)
    category = fields.String(required=False, validate=OneOf(
        ["General", "Terms", "Home", "Privacy", "Story"]))
    social_support = fields.List(
        required=False, cls_or_instance=fields.String)
