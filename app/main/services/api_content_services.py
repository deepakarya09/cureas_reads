import calendar
import time
import uuid
from http import HTTPStatus

from werkzeug.exceptions import BadRequest

from app.main import config
from app.main import db
from flask import current_app as cur_app
from app.main.models.contents import Content
from app.main.models.tags import Tag
from app.main.services.sapi_content_services import url_validator


def save_content(data):
    if Content.query.filter_by(canonical_link=data['canonical_link']).first():
        raise BadRequest("This article link already present.")

    url_validator(data['canonical_link'], "canonical link")
    url_validator(data['site_link'], 'site link')

    for tag_id in data['tag_ids']:
        tag_obj = Tag.query.filter_by(id=uuid.UUID(tag_id)).first()
        if not tag_obj:
            raise BadRequest("Tag not exist.")

    try:
        save_con = Content(
            id=uuid.uuid4(),
            title=data['title'],
            description=data['description'],
            site_link=data['site_link'],
            canonical_link=data['canonical_link'],
            image_link=data['image_link'],
            content_type_id=None if not "content_type_id" in data or data['content_type_id'] == "" or not data[
                'content_type_id'] else data['content_type_id'],
            source_id=None if not "source_id" in data or data['source_id'] == "" or not data['source_id'] else data[
                'source_id'],
            type=data['type'],
            site_name=data["site_name"],
            country=data['country'] if ("country" in data) else cur_app.config['DEFAULT_COUNTRY'],
            created_at=calendar.timegm(time.gmtime()),
            modified_at=calendar.timegm(time.gmtime())
        )
    except Exception as e:
        config.logging.warning(f"Data saving Failed {e}")
        raise BadRequest(f"Data Loading Failed")

    try:
        for tag_id in data['tag_ids']:
            tag_obj = Tag.query.filter_by(id=uuid.UUID(tag_id)).first()
            save_con.tag.append(tag_obj)
    except Exception as e:
        config.logging.warning(f"Error in tag Validation:{e}")
        raise BadRequest("Internal server error : Tag content API")

    db.session.add(save_con)
    db.session.commit()
    return save_con, HTTPStatus.CREATED.value


def get_all(page, limit):
    total = Content.query.all()
    paginated_data = Content.query.order_by(Content.created_at.desc()).paginate(page=page, per_page=limit)

    objects = paginated_data.items

    return {"items": objects,
            "total_pages": [page for page in paginated_data.iter_pages()],
            "page": page,
            "per_page": limit,
            "total": len(total)
            }, HTTPStatus.OK.value


def delete_content(id):
    try:
        content = Content.query.filter_by(id=id).first()
        db.session.delete(content)
        db.session.commit()
        return {
                   "message": "article deleted successfully.",
               }, HTTPStatus.OK.value
    except:
        return {"message": "article does not exists."}, HTTPStatus.OK.value
