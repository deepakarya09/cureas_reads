import calendar
import time
import uuid
from http import HTTPStatus

import geocoder
from flask import request
from werkzeug.exceptions import BadRequest

from app.main import config
from app.main import db
from app.main.config import MIN_SUB_ARTICLE_COUNT
from app.main.models.config_variables import ConfigVariables
from flask import current_app as cur_app
from app.main.models.submissions import Submission
from app.main.models.submitted_articles import SubmittedArticle
from app.main.models.tags import Tag
from app.main.services.sapi_content_services import url_validator, temp_save_content
from app.main.services.tags_service import post_tag


def article_count():
    total_Articles = ConfigVariables.query.filter_by(key="min_submission_article_count").first()
    if total_Articles:
        count = total_Articles.value
        return int(count)
    return MIN_SUB_ARTICLE_COUNT


def add_worker(data):
    try:
        worker = Submission(
            id=uuid.uuid4(),
            worker_id=data['workerId'],
            worker_type=data['workerType'],
            created_at=calendar.timegm(time.gmtime())
        )
    except Exception as e:
        raise BadRequest(f"Failed to save worker.")

    db.session.add(worker)
    db.session.commit()
    return worker


def crowd_source_save_worker(data):
    worker = Submission.query.filter_by(worker_id=data['workerId'], confirmation_code=None).first()

    if not worker:
        worker = add_worker(data)
        return worker, HTTPStatus.OK.value

    worker = Submission.query.filter_by(id=worker.id, confirmation_code=None).first()
    return worker, HTTPStatus.OK.value


def save_tag_crows_source(tags):
    tag_objects = []
    try:
        for tag in tags:
            tag_ob = Tag.query.filter_by(name=tag.lower()).first()
            if not tag_ob:
                tag_ob = post_tag(tag)
            tag_objects.append(tag_ob)

        return tag_objects
    except Exception as e:
        config.logging.warning(f"api: crowd_source_save tag: Failed to save tag.{e}")
        raise BadRequest(f"Failed to save tag.")


def canonical_link_validation(workerId, canonical_link):
    submissions = Submission.query.filter_by(worker_id=workerId).all()
    for sub in submissions:
        for content in sub.sub_articles:
            if content.canonical_link.strip() == canonical_link.strip():
                raise BadRequest("This article is already present.")


def crowd_source_add_article(submission_id, data):
    try:
        uuid.UUID(submission_id)
    except Exception:
        raise BadRequest("Not a valid submission ID")

    if not Submission.query.filter_by(id=submission_id).first():
        raise BadRequest("This submission id not present.")

    if not Submission.query.filter_by(worker_id=data['workerId'], id=submission_id).first():
        raise BadRequest("Not a valid workerId.")

    url_validator(data['article']['canonicalLink'], 'canonical link')
    url_validator(data['article']['siteLink'], 'site link')

    if len(SubmittedArticle.query.filter_by(submission_id=submission_id).all()) >= article_count():
        raise BadRequest("ArticleSet is already done.")

    worker = Submission.query.filter_by(id=uuid.UUID(submission_id)).first()
    sequence_number = len(worker.sub_articles) + 1
    user_ip_address = request.remote_addr
    tag_objects = save_tag_crows_source(data['article']['tags'])
    worker_geo_info = geocoder.ip(user_ip_address)
    agent = str(request.user_agent)

    try:
        save_article = SubmittedArticle(
            id=uuid.uuid4(),
            title=data['article']['title'],
            description=data['article']['description'] if data['article']['description'] else None,
            site_link=data['article']['siteLink'],
            canonical_link=data['article']['canonicalLink'],
            image_link=data['article']['imageLink'],
            type=data['article']['type'],
            country=worker_geo_info.country if worker_geo_info else cur_app.config['DEFAULT_COUNTRY'],
            submission_id=submission_id,
            city=worker_geo_info.address if worker_geo_info else None,
            user_ip=user_ip_address if user_ip_address else None,
            created_at=calendar.timegm(time.gmtime()),
            site_name=data['article']["siteName"],
            user_agent=agent if agent else None,
            sequence_number=sequence_number
        )

    except Exception as e:
        config.logging.info(f"api: crowd_source_add_article : Failed to save article.{e}")
        raise BadRequest(f"Failed to save article.{e}")

    for tag in tag_objects:
        save_article.sub_tag.append(tag)
    db.session.add(save_article)
    db.session.commit()

    if len(worker.sub_articles) == article_count():
        worker.confirmation_code = uuid.uuid4()
        worker.submitted_at = calendar.timegm(time.gmtime())
        worker.submitted_article_count = sequence_number
        db.session.commit()
        return worker, HTTPStatus.OK.value

    worker.submitted_article_count = sequence_number
    worker.modified_at = calendar.timegm(time.gmtime())
    db.session.commit()

    temp_save_content({"title": data['article']['title'], "description": data['article']['description'],
                       "image_link": data['article']['imageLink'],
                       "site_link": data['article']['siteLink'], "canonical_link": data['article']['canonicalLink'],
                       "country": worker_geo_info.country if worker_geo_info else cur_app.config['DEFAULT_COUNTRY'],
                       "site_name": data['article']["siteName"], "type": data['article']['type']}, tag_objects)

    return worker, HTTPStatus.OK.value


def extension_submission(data):
    url_validator(data['canonicalLink'], 'canonical link')
    url_validator(data['siteLink'], 'site link')

    user_ip_address = request.remote_addr
    tag_objects = save_tag_crows_source(data['tags'])
    worker_geo_info = geocoder.ip(user_ip_address)
    try:
        save_article = SubmittedArticle(
            id=uuid.uuid4(),
            title=data['title'],
            description=data['description'] if data['description'] else None,
            site_link=data['siteLink'],
            canonical_link=data['canonicalLink'],
            image_link=data['imageLink'],
            type=data['type'],
            country=worker_geo_info.country if worker_geo_info else cur_app.config['DEFAULT_COUNTRY'],
            submission_id=None,
            city=worker_geo_info.address if worker_geo_info else None,
            user_ip=user_ip_address if user_ip_address else None,
            created_at=calendar.timegm(time.gmtime()),
            site_name=data["siteName"],
            sequence_number=None
        )
    except Exception as e:
        config.logging.warning(f"api: crowd_source_add_article : Failed to save article.{e}")
        raise BadRequest(f"Failed to save article.{e}")

    for tag in tag_objects:
        save_article.sub_tag.append(tag)

    db.session.add(save_article)
    db.session.commit()

    temp_save_content({"title": data['title'], "description": data['description'],
                       "image_link": data['imageLink'],
                       "site_link": data['siteLink'], "canonical_link": data['canonicalLink'],
                       "country": worker_geo_info.country if worker_geo_info else cur_app.config['DEFAULT_COUNTRY'],
                       "site_name": data["siteName"], "type": data['type']}, tag_objects)

    return {"message": "Content successfully submitted"}, HTTPStatus.OK.value
