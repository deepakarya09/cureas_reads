import uuid
from http import HTTPStatus
from werkzeug.exceptions import BadRequest
from app.main import db, config
from app.main.models.css_styles import CssStyles
from app.main.models.template_css_styles import TemplateCssStyles
from app.main.services import get_time
from app.main.services.widget_service import upload_thumbnail


def post_css_style(data):
    if "template_css_name" not in data:
        raise BadRequest(
            "This name of template css style is not in data with key template_css_name.")
    check = TemplateCssStyles.query.filter_by(
        name=data['template_css_name']).first()
    if not check:
        raise BadRequest("Tempale css name is not available in database.")
    if CssStyles.query.filter_by(name=data['name']).first():
        raise BadRequest(
            "Css Style with this name already exist, please choose different name")
    try:
        save = CssStyles(id=uuid.uuid4(
        ), name=data['name'], template_css_id=str(check.id), description=data['description'], class_names=data['class_name'], active=data['active'], mobile_thumbnail=data['mobile_thumbnail'] if "mobile_thumbnail" in data else "", desktop_thumbnail=data['desktop_thumbnail'] if "desktop_thumbnail" in data else "", css_link=data['css_link'])
        db.session.add(save)
        db.session.commit()
        return save, HTTPStatus.CREATED
    except Exception as e:
        config.logging.critical(
            f"api: post css style : Failed to save:{e}")
        raise BadRequest("Failed to save css style.")


def get_all_css_style():
    try:
        items = CssStyles.query.all()
        return {"items": items}, HTTPStatus.OK
    except Exception as e:
        config.logging.critical(
            f"api: get all css style: Failed to load:{e}")
        raise BadRequest("Failed to load all css style.")


def get_css_style(id):
    try:
        data = CssStyles.query.filter_by(id=id).first()
        if not data:
            raise BadRequest(
                "please check id with this id data is not available.")
        return data, HTTPStatus.OK
    except Exception as e:
        config.logging.critical(
            f"api: get css style by id : Failed to load:{e}")
        raise BadRequest("Failed to load Css style.")


def delete_css_style(id):
    try:
        data = CssStyles.query.filter_by(id=id).first()
        if not data:
            raise BadRequest(
                "please check id with this id data is not available.")
        db.session.delete(data)
        db.session.commit()
        return {"message": "Css style is successfully deleted"}, HTTPStatus.OK
    except Exception as e:
        config.logging.critical(
            f"api: delete css style : Failed to Delete:{e}")
        raise BadRequest(f"Failed to delete css style.{e}")


def put_css_style(id, data):
    temp = CssStyles.query.filter_by(id=id).first()
    if not temp:
        raise BadRequest("please check id with this id data is not available.")
    if CssStyles.query.filter_by(name=data['name']).first():
        raise BadRequest(
            "Css Style with this name already exist, please choose different name")
    if "mobile_thumbnail" in data:
        try:
            thumbnail_link = upload_thumbnail(
                data['mobile_thumbnail'], str(uuid.uuid4()) + ".png")
            setattr(temp, "mobile_thumbnail", thumbnail_link)
        except:
            raise BadRequest("Not able to upload mobile thumbnail")
    if "desktop_thumbnail" in data:
        try:
            thumbnail_link = upload_thumbnail(
                data['desktop_thumbnail'], str(uuid.uuid4()) + ".png")
            setattr(temp, "desktop_thumbnail", thumbnail_link)
        except:
            raise BadRequest("Not able to upload desktop thubnail")
    try:
        for key, value in data.items():
            if key == "mobile_thumbnail" or key == "desktop_thumbnail":
                pass
            elif getattr(temp, key) != value:
                setattr(temp, key, value)
        setattr(temp, "updated_at", get_time())
        db.session.commit()
        return temp, HTTPStatus.OK
    except Exception as e:
        config.logging.critical(
            f"api: update css : Failed to update:{e}")
        raise BadRequest("Failed to update css style.")


def get_all_css_style_by_name(name):
    check = TemplateCssStyles.query.filter_by(name=name).first()
    if not check:
        raise BadRequest(
            "With this name Template Css Style is not availabe in database.")
    try:
        items = CssStyles.query.filter_by(template_css_id=str(check.id)).all()
        return {"items": items, "name": check.name, "widget_count": check.widget_count}, HTTPStatus.OK
    except Exception as e:
        config.logging.critical(
            f"api: get all css by name : Failed to update:{e}")
        raise BadRequest("Failed to get all css by name.")
