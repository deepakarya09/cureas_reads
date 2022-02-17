from flask_restplus import Namespace, fields

class User_Brand_role:
    api = Namespace("user_brand_role")

    req_for_role = api.model("Role Create", {
        "name": fields.String(required=True)
    })

    res_for_role = api.model("role Response", {
        'id':fields.String(required=True, description='UUID'),
        'name': fields.String(required=True, description='Role'),
        'created_at':fields.String(attribute="created_at", description='content creation time')
    })

    res_for_all_role = api.model("All role Response", {
        "items": fields.List(fields.Nested(res_for_role))
    })