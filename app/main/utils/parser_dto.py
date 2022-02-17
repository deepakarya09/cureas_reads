from flask_restplus import Namespace, fields


class ParserDTO:
    api = Namespace("Parser")

    req_page_replace = api.model("Replace widget request", {
        "block_no": fields.Integer(required=False),
        "name": fields.String(required=True, description="New Widget")
    })

    res_parser = api.model("Replace widget response", {
        "block_no": fields.Integer(),
        "widget_type": fields.String(),
        "widget_name": fields.String(),
        "html": fields.String()
    })

    req_image_widget_update = api.model("Image widget update", {
        "block_no": fields.Integer(),
        "image": fields.String(),
    })
