from app.main.models.brands import Brand
from app.main.services.image_upload_services import image_upload_by_url, upload_image_by_raw
import uuid

from jinja2 import Environment
from werkzeug.exceptions import BadRequest
from flask_restplus._http import HTTPStatus
from app.main import db, config
from google.cloud import storage
from app.main.models.branding_pages import BrandPages
from app.main.models.page_data import PageData
from app.main.models.widgets import Widget

storage_client = storage.Client()


def parser(html, json_data):
    try:
        template_env = Environment(cache_size=1000)
        template = template_env.from_string(html)
        parsed_html = template.render(json_data)
    except Exception as e:
        raise BadRequest(f"Error due to {e}")
    return parsed_html


def widget_replace(data):
    wid = Widget.query.filter_by(name=data['name']).first()
    if not wid:
        config.logging.warning(f"api: parser: widget not exists:")
        raise BadRequest("Widget not found!")
    return {"block_no": data['block_no'], "widget_type": wid.type, "widget_name": wid.name, "html": parser(wid.raw_html, wid.default_data)}, HTTPStatus.CREATED


def widget_parse(widget_name, data, brand_id):
    wid = Widget.query.filter_by(name=widget_name).first()
    if not wid:
        config.logging.warning(f"api: parser: widget not exists:")
        raise BadRequest("Widget not found!")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        config.logging.warning("api: parser: brand not exists:")
        raise BadRequest("Brand not found!")
    if "image" in data.keys():
        if "base64" in data["image"]:
            image_link = upload_image_by_raw(data["image"], brand_id)
            data.update({"image": image_link})
            return {"block_no": data['block_no'], "widget_type": wid.type, "widget_name": wid.name, "html": parser(wid.raw_html, data)}, HTTPStatus.CREATED
        else:
            image_link = image_upload_by_url(data["image"], brand_id)
            data.update({"image": image_link})
            return {"block_no": data['block_no'], "widget_type": wid.type, "widget_name": wid.name, "html": parser(wid.raw_html, data)}, HTTPStatus.CREATED
    else:
        return {"block_no": data['block_no'], "widget_type": wid.type, "widget_name": wid.name, "html": parser(wid.raw_html, data)}, HTTPStatus.CREATED
