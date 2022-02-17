from marshmallow import Schema, fields
from marshmallow.validate import Length


class PostSourceSchemaValidator(Schema):
    name = fields.String(required=True, validate=Length(min=1, max=50))
    website_link = fields.URL(required=True, validate=Length(min=1, max=500))
    stream_link = fields.URL(required=True, validate=Length(min=1, max=500))
    stream_type = fields.String(required=True, validate=Length(min=1, max=50))
    region = fields.List(required=True, cls_or_instance=fields.String)
    content_type = fields.List(required=True, cls_or_instance=fields.String)
    polling_interval = fields.Integer(required=True)


class PutSourceSchemaValidator(Schema):
    id = fields.UUID(required=False)
    name = fields.String(required=True, validate=Length(min=1, max=50))
    website_link = fields.URL(required=True, validate=Length(min=1, max=500))
    stream_link = fields.URL(required=True, validate=Length(min=1, max=500))
    stream_type = fields.String(required=True, validate=Length(min=1, max=50))
    region = fields.List(required=True, cls_or_instance=fields.String)
    content_type = fields.List(required=True, cls_or_instance=fields.String)
    polling_interval = fields.Integer(required=True)
