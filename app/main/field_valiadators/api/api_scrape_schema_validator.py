from marshmallow import Schema, fields


class PostScapeValidator(Schema):
    site_link = fields.URL(required=True)