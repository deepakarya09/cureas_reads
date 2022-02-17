from flask_restplus import Namespace, fields


class BrandLogsDto:
    api = Namespace("brand_log", description="Brand log API")

    user_data = api.model("user Data", {
        "id": fields.String(),
        "first_name": fields.String(),
        "last_name": fields.String(),
        "email": fields.String(),
        "image_url": fields.String(),
        "role": fields.String(),
        "verified": fields.Boolean(description='Verification of user'),
        "login_type": fields.String(attribute="login_type"),
        "first_brand_exists": fields.Boolean(),

    })

    brand_log = api.model("brand log", {
        "id": fields.String(),
        "brand_id": fields.String(),
        "user": fields.List(cls_or_instance=fields.Nested(user_data)),
        "message": fields.String(),
        "date": fields.String(),
        "created_at": fields.String()

    })
    res_brand_log = api.model('brand log response', {
        "items": fields.List(cls_or_instance=fields.Nested(brand_log))
    })
