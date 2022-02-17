from marshmallow import Schema, fields
from marshmallow.validate import Length


class TagSchemaValidator(Schema):
    name = fields.String(required=True, validate=Length(min=1, max=50))


