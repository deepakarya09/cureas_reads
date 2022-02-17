from marshmallow import Schema, fields
from marshmallow.validate import Length


class PostBrandFieldValidator(Schema):
    brand_id = fields.UUID(required=False)
    name = fields.String(required=True, allow_none=False, validate=Length(max=200))
    site_url = fields.URL(required=True, allow_none=True)
    user_id = fields.UUID(required=True, allow_none=False)
    description = fields.String(required=True, allow_none=True, validate=Length(max=1000))
    facebook_url = fields.URL(required=True, allow_none=True, validate=Length(max=1000))
    twitter_url = fields.URL(required=True, allow_none=True, validate=Length(max=1000))
    instagram_url = fields.URL(required=True, allow_none=True, validate=Length(max=1000))


class PostBrandStyleFieldValidator(Schema):
    user_id = fields.UUID(required=True, allow_none=False)
    white_theme_logo = fields.String(required=True)
    black_theme_logo = fields.String(required=True)
    colors = fields.Dict(required=True)
    fonts = fields.Dict(required=True)
    light_theme = fields.Boolean(required=True)
