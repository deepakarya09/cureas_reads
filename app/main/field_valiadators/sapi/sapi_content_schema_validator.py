from marshmallow import Schema, fields
from marshmallow.validate import Length, OneOf
from pycountry import countries


class SapiContentValidator(Schema):
    title = fields.String(required=True, validate=Length(min=10, max=1000))
    description = fields.String(required=True, validate=Length(min=10, max=1000))
    site_link = fields.String(required=True, validate=Length(max=1000))
    canonical_link = fields.URL(required=True, validate=Length(max=1000))
    image_link = fields.URL(required=True, validate=Length(max=1000))
    source_id = fields.String(required=False,)
    content_type_id = fields.String(required=False)
    status = fields.String(required=False, validate=OneOf(["", "DRAFT", "REVIEWED", "APPROVED", "PUBLISHED"]))
    type = fields.String(required=True, validate=Length(min=1, max=40))
    site_name = fields.String(required=True, validate=Length(max=200))
    tags = fields.List(required=False, cls_or_instance=fields.String(validate=Length(min=1, max=50)))
    country = fields.String(required=False, validate=OneOf([code.alpha_2 for code in countries]))
