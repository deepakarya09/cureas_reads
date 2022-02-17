from marshmallow import Schema, fields
from marshmallow.validate import Length


class workerPUTValidate(Schema):
    workerId = fields.String(required=True, allow_none=False, validate=Length(min=1, max=100))
    workerType = fields.String(required=False, allow_none=False, validate=Length(min=1, max=50))
    submittedArticleCount = fields.Integer(required=False)
    confirmationCode = fields.String(required=False,)
    createdAt = fields.Integer(required=False)
    submittedAt = fields.Integer(required=False)
    paymentStatus = fields.Boolean(required=True)
