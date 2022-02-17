from app.main.tokenvalidation.token_check import token_required
from app.main.services.multiuser_services import add_new_user_and_confirm_code, change_role_user_from_brand, email_confirmation, remove_user_from_brand
from app.main.field_valiadators.api.api_multiuser import PostEmailConfirmation, UserInputSignUp
from app.main.utils.api_multiuser_dto import MultiUser
from http import HTTPStatus
from flask import request
from flask_restplus import Resource
from werkzeug.exceptions import abort

from app.main.controllers import error_m

api = MultiUser.api

_expect_email_confirmation = MultiUser.email_request
_email_response = MultiUser.email_response
_expect_new_user = MultiUser.expect_new_user

_post_email_data_validate = PostEmailConfirmation()
_user_input_signup = UserInputSignUp()


@api.route("api/v1.0/brand/user/invite")
class SendConfirmation(Resource):
    @api.expect(_expect_email_confirmation)
    @api.marshal_with(_email_response)
    @token_required
    def post(self):
        data = request.json
        error = _post_email_data_validate.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return email_confirmation(data)

@api.route("api/v1.0/new/user/add/<confirmation>")
class SendConfirmationNewUser(Resource):
    @api.expect(_expect_new_user)
    @api.marshal_with(_email_response)
    def post(self,confirmation):
        data = request.json
        error = _user_input_signup.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return add_new_user_and_confirm_code(data,confirmation)

@api.route("api/v1.0/user/<user_id>/brand/<brand_id>/remove")
class SendConfirmationNewUser(Resource):
    @api.marshal_with(_email_response)
    @token_required
    def delete(self,user_id,brand_id):
        return remove_user_from_brand(user_id,brand_id)

@api.route("api/v1.0/user/<user_id>/brand/<brand_id>/chnage")
class ChangeRole(Resource):
    @api.marshal_with(_email_response)
    @token_required
    def put(self,user_id,brand_id):
        data = request.json
        return change_role_user_from_brand(user_id,brand_id,data)