from marshmallow import Schema, fields, ValidationError, validates
from marshmallow.validate import Length

from app.main.config import MIN_DEC_LENGTH, MIN_TAG_LENGTH, MIN_TITLE_LENGTH
from app.main.models.config_variables import ConfigVariables


def min_description_length():
    total_Articles = ConfigVariables.query.filter_by(key="min_description_length").first()
    if total_Articles:
        count = total_Articles.value
        return int(count)
    return MIN_DEC_LENGTH


def min_tags():
    total_Articles = ConfigVariables.query.filter_by(key="min_tag_length").first()
    if total_Articles:
        count = total_Articles.value
        return int(count)
    return MIN_TAG_LENGTH


def min_title_length():
    total_Articles = ConfigVariables.query.filter_by(key="min_title_length").first()
    if total_Articles:
        count = total_Articles.value
        return int(count)
    return MIN_TITLE_LENGTH


class article_validator(Schema):
    title = fields.String(required=True)
    description = fields.String(required=True)
    siteLink = fields.URL(required=True)
    canonicalLink = fields.URL(required=True)
    imageLink = fields.URL(required=False)
    type = fields.String(required=False, validate=Length(max=40))
    country = fields.String(required=False, validate=Length(max=30))
    city = fields.String(required=False, validate=Length(max=100))
    userIP = fields.String(required=False, validate=Length(max=20))
    siteName = fields.String(required=True, validate=Length(max=200))
    tags = fields.List(required=False, cls_or_instance=fields.String(validate=Length(min=1, max=50)))

    @validates('title')
    def validate_min_title_length(self, title):
        if len(title.split()) < min_title_length():
            raise ValidationError([f"Minimum words required {min_title_length()}."])
        if len(title) > 1000:
            raise ValidationError([f"Length must be between 1 and 1000."])

    @validates('description')
    def validate_min_description_length(self, description):
        if len(description.split()) < min_description_length():
            raise ValidationError([f"Minimum words required {min_description_length()}."])
        if len(description) > 1000:
            raise ValidationError([f"Length must be between 1 and 1000."])

    @validates('tags')
    def validate_min_tag_length(self, tags):
        if len(tags) < min_tags():
            raise ValidationError([f"Minimum required {min_tags()}."])


class CrowdSourcePost(Schema):
    workerId = fields.String(required=True, validate=Length(min=1, max=100))
    article = fields.Nested(article_validator, required=True)


class WorkerSubmission(Schema):
    workerId = fields.String(required=True, validate=Length(min=1, max=100))
    workerType = fields.String(required=True, validate=Length(min=1, max=50))
