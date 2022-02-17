from marshmallow import Schema, fields
from marshmallow.validate import Length


class ConfigSchemaValidator(Schema):
    key = fields.String(required=True, validate=Length(min=1, max=500))
    value = fields.String(required=True, validate=Length(min=1, max=100))


class PUTConfigSchemaValidator(Schema):
    value = fields.String(required=True, validate=Length(min=1, max=100))
