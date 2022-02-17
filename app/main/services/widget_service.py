from sqlalchemy.sql.elements import Null
from app.main.models.faq_model import FaqWidgit
from app.main.models.pricing_model import PricingWidgit
import base64
from re import template
from app.main.gcp_clients.bucket import upload_bucket
import uuid
from flask import current_app as cur_app
from flask_restplus._http import HTTPStatus
from werkzeug.exceptions import BadRequest

from app.main import db, config
from app.main.models.widget_tag import WidgetTag
from app.main.models.widgets import Widget
from app.main.models.widgets_with_tags import WidgetsWithTags
from app.main.services import get_time
from app.main.services.parser_service import parser


def upload_thumbnail(image_data, file):
    try:
        image_data = base64.b64decode(image_data.split(",")[1])
    except Exception:
        raise BadRequest("Incorrect image format")
    try:
        upload_bucket(bytes_im=image_data,
                      remote_path=cur_app.config["THUMBNAIL"] + file)
        cdn_image_link = cur_app.config["BUCKET_BASE_URL"] + \
            cur_app.config["THUMBNAIL"] + file
        return cdn_image_link
    except Exception as e:
        raise BadRequest(
            "Not able to upload thubnail Please check thumbnail input {e}")


def return_dict(widget):
    alltags = WidgetsWithTags.query.filter_by(widget_id=widget.id).all()
    tags = []
    if alltags:
        for i in alltags:
            tagname = WidgetTag.query.filter_by(id=i.tag_id).first()
            tags.append(tagname.name)
    return {"id": widget.id, "name": widget.name, "html": parser(widget.raw_html, widget.default_data),
            'created_at': widget.created_at,
            "updated_at": widget.updated_at,
            "category": widget.category,
            "thumbnail": widget.thumbnail,
            "type": widget.type,
            "tags": tags
            }


def save_widget(data):
    if Widget.query.filter_by(name=data['name']).first():
        raise BadRequest(
            "Widget with this name already exist, please choose different name")
    try:
        thumbnail_link = upload_thumbnail(
            data['thumbnail'], str(uuid.uuid4()) + ".png")
    except Exception as e:
        raise BadRequest(
            "Not able to upload thubnail Please check thumbnail input {e}")
    widget = Widget(id=uuid.uuid4(), name=data['name'], raw_html=data['raw_html'],
                    default_data=data['default_data'],
                    category=data['category'],
                    type=data['type'],
                    created_at=get_time(), thumbnail=thumbnail_link)

    db.session.add(widget)
    if "tag" in data:
        tag = WidgetTag.query.filter_by(name=data['tag']).first()
        if not tag:
            raise BadRequest(
                "Given tag is not available in database please add it or change tag")
        check = WidgetsWithTags.query.filter(
            WidgetsWithTags.widget_id == widget.id, WidgetsWithTags.tag_id == tag.id).first()
        if check:
            raise BadRequest(
                "Given tag is already added to this please change tag")
        connect = WidgetsWithTags(
            widget_id=widget.id,
            tag_id=tag.id
        )
        db.session.add(connect)
    db.session.commit()
    return return_dict(widget), HTTPStatus.CREATED


def save_widget_tag(data):
    if "name" not in data:
        raise BadRequest("Please add name of tag")
    if WidgetTag.query.filter_by(name=data['name']).first():
        raise BadRequest(f"{data['name']} already exists")
    try:
        save = WidgetTag(
            id=uuid.uuid4(), name=data['name']
        )
        db.session.add(save)
        db.session.commit()
        return save, HTTPStatus.CREATED
    except Exception as e:
        config.logging.critical(f"Failed to add widget Tag:{e}")
        raise BadRequest("Failed to add widget Tag")


def get_all_widget_tag():
    try:
        items = WidgetTag.query.all()
        return {"items": items}, HTTPStatus.OK
    except Exception as e:
        config.logging.critical(f"Failed to get all widget Tag:{e}")
        raise BadRequest("Failed to get all widget Tag")


def update_widget_tag(tag_id, data):
    widgettag = WidgetTag.query.filter_by(id=tag_id).first()
    if not widgettag:
        raise BadRequest("Widget Tag not found !")
    try:
        for key, value in data.items():
            if getattr(widgettag, key) != value:
                setattr(widgettag, key, value)
    except Exception as e:
        config.logging.critical(f"Failed to updated widget:{e}")
        raise BadRequest("Update Failed")
    db.session.commit()
    return widgettag, HTTPStatus.OK


def delete_widget_tag(tag_id):
    widgettag = WidgetTag.query.filter_by(id=tag_id).first()
    if not widgettag:
        raise BadRequest("Widget Tag not found !")
    db.session.delete(widgettag)
    db.session.commit()
    return {"message": "Widget Deleted Successfully"}, HTTPStatus.OK


def remove_widget_tag(widget_id, tag_id):
    widgettag = WidgetsWithTags.query.filter(
        WidgetsWithTags.widget_id == widget_id, WidgetsWithTags.tag_id == tag_id).first()
    if not widgettag:
        raise BadRequest("Widget Tag not found !")
    db.session.delete(widgettag)
    db.session.commit()
    return {"message": "Widget Tag Removed Successfully"}, HTTPStatus.OK


def delete_widget(id):
    widget = Widget.query.filter_by(id=id).first()
    if not widget:
        raise BadRequest("Widget not found !")
    db.session.delete(widget)
    db.session.commit()
    return {"message": "Widget Deleted Successfully"}, HTTPStatus.OK


def update_widget(id, data):
    widget = Widget.query.filter_by(id=id).first()
    if not widget:
        raise BadRequest("Widget not found !")
    if "category" in data:
        if not (data['category'] == "General" or data['category'] == "Privacy" or data['category'] == "Terms" or data['category'] == "Home" or data['category'] == "Story"):
            raise BadRequest(
                "please enter valid category, General , Privacy , Terms , Home or Story!")
    if "thumbnail" in data:
        try:
            thumbnail_link = upload_thumbnail(
                data['thumbnail'], str(uuid.uuid4()) + ".png")
            setattr(widget, "thumbnail", thumbnail_link)
        except:
            raise BadRequest("Not able to upload thubnail")
    if "tag" in data:
        tag = WidgetTag.query.filter_by(name=data['tag']).first()
        if not tag:
            raise BadRequest(
                "Given tag is not available in database please add it or change tag")
        check = WidgetsWithTags.query.filter(
            WidgetsWithTags.widget_id == widget.id, WidgetsWithTags.tag_id == tag.id).first()
        if check:
            raise BadRequest(
                "Given tag is already added to this widget please change tag")
        connect = WidgetsWithTags(
            widget_id=widget.id,
            tag_id=tag.id
        )
        db.session.add(connect)
    if "name" in data:
        check = Widget.query.filter_by(name=data["name"]).first()
        if check:
            raise BadRequest(
                f"This name of widget is already available in database")
    try:
        for key, value in data.items():
            if key == "thumbnail" or key == "tag":
                pass
            elif getattr(widget, key) != value:
                setattr(widget, key, value)
        setattr(widget, "updated_at", get_time())
    except Exception as e:
        config.logging.critical(f"Failed to updated widget:{e}")
        raise BadRequest("Update Failed")
    db.session.commit()
    return return_dict(widget), HTTPStatus.OK


def get_widget(id):
    widget = Widget.query.filter_by(id=id).first()
    if not widget:
        raise BadRequest("Widget not found !")
    return return_dict(widget), HTTPStatus.OK


def get_all_widgets(size, category):
    if category and size == None:
        if not (category == "General" or category == "Privacy" or category == "Terms" or category == "Home" or category == "Story"):
            config.logging.warning(
                f"api: get all widgit: please enter valid status!")
            raise BadRequest(
                "please enter valid key, General , Privacy , Terms , Home or Story!")
        items = Widget.query.filter(Widget.category == category).order_by(
            Widget.created_at.desc()).all()

    elif size and category == None:
        tag = WidgetTag.query.filter_by(name=size).first()
        if not tag:
            raise BadRequest("This size is not available in database")
        items = Widget.query.join(WidgetsWithTags).filter(
            WidgetsWithTags.tag_id == tag.id).order_by(Widget.created_at.desc()).all()
    elif category and size:
        tag = WidgetTag.query.filter_by(name=size).first()
        if not tag:
            raise BadRequest("This size is not available in database")
        data = Widget.query.join(WidgetsWithTags).filter(
            WidgetsWithTags.tag_id == tag.id).order_by(Widget.created_at.desc())
        items = data.filter(Widget.category == category).all()
    else:
        items = Widget.query.order_by(Widget.created_at.desc()).all()
    return {"items": [return_dict(widget) for widget in items]}, HTTPStatus.OK


def save_pricing_widget(data):
    try:
        pricing_widget = PricingWidgit(
            id=uuid.uuid4(),
            title=data['title'] if "title" in data else None,
            subtitle=data['subtitle'] if 'subtitle' in data else None,
            brand_id=data['brand_id'] if 'brand_id' in data else None,
            point_1=data['point_1'] if 'point_1' in data else None,
            point_2=data['point_2'] if 'point_2' in data else None,
            point_3=data['point_3'] if 'point_3' in data else None,
            point_4=data['point_4'] if 'point_4' in data else None,
            point_5=data['point_5'] if 'point_5' in data else None,
            point_6=data['point_6'] if 'point_6' in data else None,
            point_7=data['point_7'] if 'point_7' in data else None,
            point_8=data['point_8'] if 'point_8' in data else None,
            point_9=data['point_9'] if 'point_9' in data else None,
            point_10=data['point_10'] if 'point_10' in data else None,
            button=data['button'] if 'button' in data else None
        )
        db.session.add(pricing_widget)
        db.session.commit()
    except Exception as e:
        raise BadRequest(f"Error in saving Data {e}")
    return pricing_widget, HTTPStatus.CREATED


def delete_pricing_widget(id):
    pricing_widget = PricingWidgit.query.filter_by(id=id).first()
    if not pricing_widget:
        raise BadRequest("Pricing Widget not found !")
    db.session.delete(pricing_widget)
    db.session.commit()
    return {"message": "Pricing Widget Deleted Successfully"}, HTTPStatus.OK


def get_all_pricing_widgets():
    all_widgets = PricingWidgit.query.order_by(PricingWidgit.created_at).all()
    return {"items": all_widgets}, HTTPStatus.OK


def get_pricing_widget(id):
    pricing_widget = PricingWidgit.query.filter_by(id=id).first()
    if not pricing_widget:
        raise BadRequest("Pricing Widget not found !")
    return pricing_widget, HTTPStatus.OK


def update_pricing_widget(id, data):
    pricing_widget = PricingWidgit.query.filter_by(id=id).first()
    if not pricing_widget:
        raise BadRequest("Pricing Widget not found !")
    try:
        for key, value in data.items():
            if getattr(pricing_widget, key) != value:
                setattr(pricing_widget, key, value)
    except Exception as e:
        config.logging.critical(f"Failed to updated widget:{e}")
        raise BadRequest("Update Failed")
    db.session.commit()
    return pricing_widget, HTTPStatus.OK


def save_faq_widget(data):
    try:
        faq_widget = FaqWidgit(
            id=uuid.uuid4(),
            data=data["data"]
        )
        db.session.add(faq_widget)
        db.session.commit()
    except Exception as e:
        raise BadRequest(f"Error in saving Data {e}")
    return faq_widget, HTTPStatus.CREATED


def delete_faq_widget(id):
    faq_widget = FaqWidgit.query.filter_by(id=id).first()
    if not faq_widget:
        raise BadRequest("Faq Widget not found !")
    db.session.delete(faq_widget)
    db.session.commit()
    return {"message": "faq Widget Deleted Successfully"}, HTTPStatus.OK


def get_all_faq_widgets():
    all_widgets = FaqWidgit.query.order_by(FaqWidgit.created_at).all()
    return {"items": all_widgets}, HTTPStatus.OK


def get_faq_widget(id):
    faq_widget = FaqWidgit.query.filter_by(id=id).first()
    if not faq_widget:
        raise BadRequest("Faq Widget not found !")
    return faq_widget, HTTPStatus.OK


def update_faq_widget(id, data):
    faq_widget = FaqWidgit.query.filter_by(id=id).first()
    if not faq_widget:
        raise BadRequest("Faq Widget not found !")
    try:
        for key, value in data.items():
            if getattr(faq_widget, key) != value:
                setattr(faq_widget, key, value)
    except Exception as e:
        config.logging.critical(f"Failed to updated widget:{e}")
        raise BadRequest("Update Failed")
    db.session.commit()
    return faq_widget, HTTPStatus.OK
