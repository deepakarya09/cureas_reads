from flask_restplus import Namespace, fields


class generator:
    api = Namespace("iapi", description="API")
    re_gen_content = api.model("generator", {
        "id": fields.String(description='uuid'),
        "title": fields.String(description='title of content'),
        "description": fields.String(description='description of content'),
        "site_link": fields.String(description='site link of content'),
        "canonical_link": fields.String(description='image URL of content'),
        "image_link": fields.String(attribute="cdn_image_link", description='image URL of content'),
        "site_name": fields.String(description='site name of content'),
        "type": fields.String(description='type of content'),
        "country": fields.String(description='country of content'),
        "used": fields.String(description='used of content')

    })

    res_all_content = api.model('response of all sources', {
        'items': fields.List(fields.Nested(re_gen_content)),
    })
