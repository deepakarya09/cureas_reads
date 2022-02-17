from app.main.tokenvalidation.token_check import token_required
from app.main.services.referral_services import create_referral
from app.main.utils.referral_code import RefferalCode
from flask_restplus import Resource
from flask import request

api = RefferalCode.api

_req_for_referral = RefferalCode.req_for_referral
_res_for_referral = RefferalCode.res_for_referral

@api.route("api/v1.0/user/referral/create")
class ReferralCodeCreate(Resource):
    @api.expect(_req_for_referral)
    @api.marshal_with(_res_for_referral)
    @token_required
    def post(self):
        return create_referral(data=request.json)