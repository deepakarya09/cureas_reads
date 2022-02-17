from flask_restplus import Namespace, fields


class tagDto:
    api = Namespace("Tag", description="Tag Operations")
    req_tag = api.model('tag post request', {
        'name': fields.String(required=True, description='tag')
    })
    res_tag = api.model("tag post response", {
        "id": fields.String(description='uuid of tag'),
        "name": fields.String(description='tag')
    })

    res_all = api.model("Get All tags", {
        "items": fields.List(fields.Nested(res_tag))
    })
