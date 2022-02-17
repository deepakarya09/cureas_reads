

from app.main.services.user_registration_confirmation_mail import confirm_email, send_email
from http import HTTPStatus
from flask import request
from flask_restplus import Resource
from werkzeug.exceptions import abort

from app.main.controllers import error_m
from app.main.field_valiadators.aapi.aapi_user_schema_validator import UserInputSchemaSignUp, UserInputSchemaSignIn, \
    LoginFieldValidator
from app.main.services.user_service import change_password, forget_password_notification, sign_up, sign_in, login
from app.main.utils.user_dto import UserDto

api = UserDto.api

_req_user_info = UserDto.req_user_info
_req_user_auth = UserDto.req_user_auth
_return_sign_in = UserDto.return_sign_in
res_user_info = UserDto.res_user_info
_email_verification_request = UserDto.req_email_verification
_google_login_request = UserDto.login_request
_login_response = UserDto.login_response
_response_message = UserDto.response_message
_req_for_channge_password = UserDto.req_for_channge_password

_user_signup = UserInputSchemaSignUp()
_user_signin = UserInputSchemaSignIn()


@api.route("aapi/v1.0/signup")
class admin_signup(Resource):
    @api.expect(_req_user_info)
    @api.marshal_with(res_user_info)
    def post(self):
        """Add new user to database"""
        data = request.json
        error = _user_signup.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return sign_up(data=data, invitaion=False)


@api.route("aapi/v1.0/signin")
class admin_signin(Resource):
    @api.expect(_req_user_auth)
    @api.marshal_with(_return_sign_in)
    def post(self):
        """Login"""
        data = request.json
        error = _user_signin.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        data['login_type'] = 'system'
        return sign_in(data=data)


@api.route("aapi/v1.0/login")
class google_login(Resource):
    @api.expect(_google_login_request)
    @api.marshal_with(_login_response)
    def post(self):
        validator = LoginFieldValidator()
        data = request.json
        error = validator.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return login(request.json)


@api.route("aapi/v1.0/send_email")
class token_confirmation(Resource):
    @api.expect(_email_verification_request)
    def post(self):
        data = request.json
        email = data['email']
        return send_email(email)


@api.route("aapi/v1.0/confirm_email/<token>")
class token_confirmation(Resource):
    def get(self, token):
        return confirm_email(token)


@api.route("aapi/v1.0/forget_password")
class forget_password(Resource):
    @api.marshal_with(_response_message)
    @api.expect(_email_verification_request)
    def post(self):
        data = request.json
        email = data['email']
        return forget_password_notification(email)


@api.route("aapi/v1.0/chnage_password/<confirm_code>")
class token_confirmation(Resource):
    @api.expect(_req_for_channge_password)
    @api.marshal_with(_response_message)
    def post(self, confirm_code):
        data = request.json
        return change_password(data=data, confirm_code=confirm_code)
