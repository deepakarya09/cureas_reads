import uuid
from http import HTTPStatus
from werkzeug.exceptions import BadRequest
from app.main import db, config
from app.main.models.css_styles import CssStyles
from app.main.models.template_css_styles import TemplateCssStyles
from app.main.models.widgets_with_tags import WidgetsWithTags
from app.main.services import get_time


def post_template_css_style(data):
    if "name" not in data:
        raise BadRequest("Please add name in data filed.")
    check = TemplateCssStyles.query.filter_by(name=data['name']).first()
    if check:
        raise BadRequest("This name of css style is already available.")
    try:
        save = TemplateCssStyles(id=uuid.uuid4(
        ), name=data['name'], widget_count=data['widget_count'], description=data['description'])
        db.session.add(save)
        db.session.commit()
        return save, HTTPStatus.CREATED
    except Exception as e:
        config.logging.critical(
            f"api: post template css : Failed to save:{e}")
        raise BadRequest("Failed to save Template css style.")


def get_all_template_css_style():
    try:
        data = TemplateCssStyles.query.all()
        items = []
        if data:
            for i in data:
                da = {
                    "id": i.id,
                    "description": i.description,
                    "widget_count": i.widget_count,
                    "name": i.name,
                    "created_at": i.created_at,
                    "updated_at": i.updated_at,
                    "css_styles": CssStyles.query.filter_by(template_css_id=i.id).order_by(CssStyles.created_at.desc()).all()
                }
                items.append(da)
        return {"items": items}, HTTPStatus.CREATED
    except Exception as e:
        config.logging.critical(
            f"api: get all template css : Failed to load:{e}")
        raise BadRequest("Failed to load all template css style.")


def get_template_css_style(id):
    try:
        data = TemplateCssStyles.query.filter_by(id=id).first()
        if not data:
            raise BadRequest(
                "please check id with this id data is not available.")
        return data, HTTPStatus.CREATED
    except Exception as e:
        config.logging.critical(
            f"api: get template css by id : Failed to load:{e}")
        raise BadRequest(f"Failed to load template css style.{e}")


def delete_template_css_style(id):
    try:
        data = TemplateCssStyles.query.filter_by(id=id).first()
        if not data:
            raise BadRequest(
                "please check id with this id data is not available.")
        db.session.delete(data)
        db.session.commit()
        return {"message": "Template css style is successfully deleted"}, HTTPStatus.CREATED
    except Exception as e:
        config.logging.critical(
            f"api: delete template css : Failed to Delete:{e}")
        raise BadRequest("Failed to delete template css style.")


def put_template_css_style(id, data):
    check = TemplateCssStyles.query.filter_by(name=data['name']).first()
    if check:
        raise BadRequest("This name of css style is already available.")
    try:
        temp = TemplateCssStyles.query.filter_by(id=id).first()
        if not temp:
            raise BadRequest(
                "please check id with this id data is not available.")
        for key, value in data.items():
            if getattr(temp, key) != value:
                setattr(temp, key, value)
        setattr(temp, "updated_at", get_time())
        db.session.commit()
        return temp, HTTPStatus.OK
    except Exception as e:
        config.logging.critical(
            f"api: update template css : Failed to update:{e}")
        raise BadRequest("Failed to update template css style.")
