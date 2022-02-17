from marshmallow import Schema, fields
from marshmallow.validate import Length


class apiBrandArticleValidator(Schema):
    title = fields.String(required=True)
    description = fields.String(required=True)
    canonical_link = fields.URL(required=True)
    image_link = fields.String(required=True)
    content_type = fields.String(required=True, validate=Length(min=1, max=40))
    site_name = fields.String(required=False, validate=Length(max=200))
    tags = fields.List(required=False, cls_or_instance=fields.String(validate=Length(min=1, max=50)))
    favicon_icon_link = fields.String(required=False)