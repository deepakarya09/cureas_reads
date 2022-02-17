from flask_restplus import Namespace, fields


class ScrapDto:
    api = Namespace("scraps", description="Content API")

    req_link = api.model('send Link to scrape', {
        "site_link": fields.String(description="site_link")
    })
    res_link = api.model("response of scrape", {
        "title": fields.String(description="title"),
        "description": fields.String(description="description"),
        "canonical_link": fields.String(description="canonical link"),
        "image_link": fields.String(description="image link"),
        "type": fields.String(description="type"),
        "site_name": fields.String(description="site name"),
        "favicon_icon_link": fields.String(description="favicon_icon_link")
    })
