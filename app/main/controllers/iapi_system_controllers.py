from http import HTTPStatus

from flask import request
from flask_restplus import Resource
from werkzeug.exceptions import abort

from app.main.controllers import error_m
from app.main.field_valiadators.iapi.iapi_config_schema_validator import ConfigSchemaValidator, PUTConfigSchemaValidator
from app.main.services.iapi_system_services import get_all_config_vars, validation, update_config_var, delete_config_var
from app.main.utils.config_variables_dto import ConfigVarsDto

api = ConfigVarsDto.api
_req_config_variable = ConfigVarsDto.req_config_variable
_res_for_put = ConfigVarsDto.res_for_put
_res_config = ConfigVarsDto.res_config
_res_all_config_variables = ConfigVarsDto.res_all_config_variables

_validator = ConfigSchemaValidator()
_put_validator = PUTConfigSchemaValidator()


@api.route("iapi/v1.0/system/config")
class PostConfigVar(Resource):
    @api.marshal_with(_res_config)
    def post(self):
        data = request.json
        error = _validator.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return validation(data)


@api.route("iapi/v1.0/system/config/<key>")
class PutConfigVar(Resource):
    @api.marshal_with(_res_for_put)
    def put(self, key):
        data = request.json
        error = _put_validator.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return update_config_var(key, data)


@api.route("iapi/v1.0/system/config")
class GetConfigVar(Resource):
    @api.marshal_with(_res_all_config_variables)
    def get(self):
        return get_all_config_vars()


@api.route("iapi/v1.0/system/config/<key>")
class DeleteConfigVar(Resource):
    def delete(self, key):
        return delete_config_var(key)
