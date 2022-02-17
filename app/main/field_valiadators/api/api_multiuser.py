from marshmallow import Schema, fields
from marshmallow.validate import Length, Email, OneOf


class PostEmailConfirmation(Schema):
    brand_id = fields.UUID(required=True)
    email = fields.Email(required=True, allow_none=False, validate=Length(max=200))

class UserInputSignUp(Schema):
    password = fields.String(required=False)