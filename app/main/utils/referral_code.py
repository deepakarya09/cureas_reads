from flask_restplus import Namespace, fields

class RefferalCode:
    api = Namespace("referral")

    req_for_referral = api.model("Referral Code Create", {
        "count": fields.Integer(required=False),
        'created_by': fields.String(required=True, description='UUID')
    })

    res_for_referral = api.model("Referral Code Response", {
        'id':fields.String(required=True, description='UUID'),
        "count": fields.Integer(required=False),
        'created_by': fields.String(required=True, description='UUID'),
        "code": fields.String(required=True, description="referral code"),
        'created_at':fields.String(attribute="created_at", description='content creation time')
    })
    