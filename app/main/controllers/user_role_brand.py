from app.main.services.create_user_role import all_role, create_role
from app.main.utils.user_brand_role import User_Brand_role
from flask_restplus import Resource
from flask import request

api = User_Brand_role.api

_req_for_role = User_Brand_role.req_for_role
_res_for_role = User_Brand_role.res_for_role
_res_for_all_role = User_Brand_role.res_for_all_role

@api.route("api/v1.0/user/brand/role/create")
class RoleCreate(Resource):
    @api.expect(_req_for_role)
    @api.marshal_with(_res_for_role)
    def post(self):
        return create_role(data=request.json)
    
@api.route("api/v1.0/user/brand/roles")
class GetAllRole(Resource):
    @api.marshal_with(_res_for_all_role)
    def get(self):
        return all_role()