import uuid
from http import HTTPStatus

from werkzeug.exceptions import BadRequest

from app.main import db, config
from app.main.models.tags import Tag


def post_tag(_tag):
    try:
        tag = Tag(id=uuid.uuid4(), name=_tag.lower())
        db.session.add(tag)
        db.session.commit()
        return tag
    except Exception as e:
        config.logging.critical(f"api: source details : Failed to save tag:{e}")
        raise BadRequest("Failed to save tag.")


def tags(data):
    _tag = data['name']
    tag = Tag.query.filter_by(name=_tag.lower()).first()
    if tag:
        raise BadRequest("Tag already exist.")
    tag = post_tag(_tag)
    return tag, HTTPStatus.CREATED.value


def get_all():
    return {"items": Tag.query.all()}, HTTPStatus.OK.value
