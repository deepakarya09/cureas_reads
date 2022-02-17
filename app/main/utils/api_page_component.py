from flask_restplus import Namespace, fields


class PageComponentAPI:
    api = Namespace("PageComponent", description="page component API")
    get_response_for_brand = api.model("response for get api", {
        "id": fields.String(),
        "default_html": fields.String(required=True, description='Brand_id to add'),
        "parsed_html": fields.String(required=True, description='Parsed html'),
        "name": fields.String(),
        "active": fields.Boolean()

    })

    get_all_component_response = api.model("response for get all component", {
        "items": fields.List(fields.Nested(get_response_for_brand)),
        "cssLink": fields.String(required=True, description='css link')
    })

    get_page_component = api.model("get page component", {
        "id": fields.String(),
        "name": fields.String(),
        "data": fields.String(),
        "category": fields.String(),
        "active": fields.Boolean(),
    })
    post_page_component = api.model("post page component", {
        "name": fields.String(),
        "data": fields.String(),
        "category": fields.String(),
        "active": fields.Boolean(required=False)
    })
    put_page_component_request = api.model("put page component", {
        "name": fields.String(required=False),
        "data": fields.String(required=False),
        "category": fields.String(required=False),
        "active": fields.Boolean(required=False)
    })
    post_data_for_brand = api.model("post data component for brand", {
        "edited_html": fields.String(required=True),
        "id": fields.String()
    })
    response_for_saved_data = api.model("response after save data", {
        "message": fields.String()
    })
