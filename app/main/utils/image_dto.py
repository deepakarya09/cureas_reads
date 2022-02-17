from flask_restplus import Namespace, fields


class ImageDto:
    api = Namespace("Get layout", description="layout")

    req_image_link = api.model("request image link", {
        "link": fields.String(required=True, description="image link")
    })

    res_image_data = api.model("response image data",{
        "data": fields.String(required=True, description="image data")
    })