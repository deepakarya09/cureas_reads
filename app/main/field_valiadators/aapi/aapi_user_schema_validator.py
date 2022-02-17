from marshmallow import Schema, fields
from marshmallow.validate import Length, Email, OneOf


class UserInputSchemaSignUp(Schema):
    first_name = fields.String(required=False, allow_none=False)
    last_name = fields.String(required=False)
    email = fields.String(required=True, validate=Email())
    image_url = fields.String(required=False, allow_none=True)
    password = fields.String(required=False)
    referral_code = fields.String(required=False)
    token = fields.String(required=False, allow_none=True)
    login_type = fields.String(required=True, OneOf=["google", "system", "apple"])
    role = fields.String(required=False, validate=OneOf(choices=["admin", "editor"]))


class UserInputSchemaSignIn(Schema):
    email = fields.String(required=True, validate=Email())
    password = fields.String(required=True)


class LoginFieldValidator(Schema):
    first_name = fields.String(required=False, allow_none=False)
    last_name = fields.String(required=False, allow_none=False)
    email = fields.Email(required=True, allow_none=False, validate=Length(max=100))
    image_url = fields.String(required=False, allow_none=False)
    token = fields.String(required=False, allow_none=True)
    login_type = fields.String(required=True, allow_none=False, validate=OneOf(["google", "apple", "system"]))
    password = fields.String(required=False)
