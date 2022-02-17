import calendar
import time
import uuid
from http import HTTPStatus

from sqlalchemy import or_
from werkzeug.exceptions import BadRequest

from app.main import config
from app.main import db
from app.main.models.source import Source
from app.main.services.sapi_content_services import url_validator


def add_source(data):
    try:
        name = data['name']
        website_link = data['website_link']
        stream_link = data['stream_link']
        stream_type = data['stream_type']
        content_type = data['content_type'] if data['content_type'] else []
        polling_interval = data['polling_interval']
        region = data['region']
    except Exception as e:
        config.logging.critical(f"Input fields not found {e}")
        raise BadRequest("Input fields not found.")

    url_validator(website_link, 'website link')

    source = Source.query.filter_by(stream_link=stream_link).first()
    seq = calendar.timegm(time.gmtime())

    if source:
        raise BadRequest("Source already exist.")

    source = Source(id=uuid.uuid4(), name=name, website_link=website_link, stream_type=stream_type,
                    stream_link=stream_link, polling_interval=polling_interval, content_type=content_type,
                    region=region, updated_at=seq, created_at=seq)
    add_commit(source)

    return source, HTTPStatus.CREATED.value


def source_get(page, limit, searchKey):
    if searchKey:
        search = "%{}%".format(searchKey)
        paginated_data = Source.query.order_by(
            Source.created_at.desc()).filter(or_(Source.name.ilike(search), Source.stream_type.ilike(search))).paginate(page=page, per_page=limit)
        objects = paginated_data.items
    else:
        paginated_data = Source.query.order_by(
            Source.created_at.desc()).paginate(page=page, per_page=limit)
        objects = paginated_data.items

    return {"items": objects,
            "page": paginated_data.page,
            "per_page": paginated_data.per_page,
            "total": paginated_data.total,
            "total_pages": [page for page in paginated_data.iter_pages()],
            }, HTTPStatus.OK.value


def update_source(source_id, data):
    try:
        source = Source.query.filter_by(id=uuid.UUID(source_id)).first()
    except Exception as e:
        raise BadRequest("source not exists.")
    if not source:
        raise BadRequest("source not exists.")
    try:
        source.name = data['name']
        source.website_link = data['website_link']
        source.stream_link = data['stream_link']
        source.stream_type = data['stream_type']
        source.content_type = data['content_type']
        source.polling_interval = data['polling_interval']
        source.region = data['region']
        source.updated_at = calendar.timegm(time.gmtime())
    except Exception as e:
        config.logging.critical(f"api: source details : Field is missing. {e}")
        raise BadRequest("Field to save.")
    db.session.commit()

    return source, HTTPStatus.OK.value


def get_specific_source(source_id):
    try:
        source_id = uuid.UUID(source_id)
    except Exception as e:
        raise BadRequest("Invalid Source Id.")
    source = Source.query.filter_by(id=source_id).first()
    if not source:
        raise BadRequest("Source not exists.")
    return source, HTTPStatus.OK.value


def delete_source(id):
    try:
        source = Source.query.filter_by(id=id).first()
        db.session.delete(source)
        db.session.commit()
        config.logging.info(f"source delete completed:{source.website_link}")
        return {
            "message": "Source deleted successfully.",
        }, 200

    except Exception as e:
        config.logging.info(f"source not found:{e}")
        return {"message": "Source does not exists."}, 200


def add_commit(info):
    db.session.add(info)
    db.session.commit()
