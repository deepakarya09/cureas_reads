from email import message
from app.main.models.brand_log import BrandLog
from app.main.services.image_upload_services import image_upload_by_url, upload_image_by_raw
from http import HTTPStatus
import calendar
import time
from sqlalchemy import or_
import requests
from app.main.models.brand_articles import BrandContent
from app.main.models.user import User
from app.main.models.user_session import UserSession
from flask import request
from app.main.models.brands import Brand
from werkzeug.exceptions import BadRequest, Forbidden
from app.main import config, db
import uuid
from flask import current_app as cur_app
from datetime import date


def getuser():
    headers = request.headers
    bearer = headers.get('Authorization')
    if not bearer:
        raise Forbidden("Token not Found")
    token = bearer.split()[1]
    sess = UserSession.query.filter_by(token=token).first()
    ids = sess.session.id
    return ids


def post_article(data, brand_id):
    try:
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(
            f"Api: Post article : Invalid submission - brand Id: {brand_id}.")
        raise BadRequest(f"This {brand_id} - Brand id is not valid.")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        raise BadRequest(
            "Brand not available in database. Please check brand id.")
    userid = getuser()
    user = User.query.filter_by(id=userid).first()
    if not user:
        config.logging.warning(
            f"Api: Post article : Invalid user id : {userid}.")
        raise BadRequest(
            "User not found in database.Please login or create account.")
    if "image_link" in data.keys():
        if "base64" in data["image_link"]:
            image_link = upload_image_by_raw(data["image_link"], brand_id)
        else:
            image_link = image_upload_by_url(data["image_link"], brand_id)
    if "tags" in data.keys() and data["tags"] != None:
        tags = data["tags"]
    else:
        tags = []
    try:
        save_article = BrandContent(
            id=uuid.uuid4(),
            user_id=user.id,
            brand_id=brand_id,
            title=data['title'],
            description=data['description'],
            canonical_link=data['canonical_link'],
            image_link=image_link,
            tags=tags,
            content_type=data['content_type'],
            site_name=data["site_name"],
            favicon_icon_link=data['favicon_icon_link'] if data['favicon_icon_link'] else cur_app.config["DEFAULT_WIDGET_BLANK_IMAGE"],
            created_at=calendar.timegm(time.gmtime()),
            updated_at=calendar.timegm(time.gmtime())
        )
        db.session.add(save_article)
        log = BrandLog(id=uuid.uuid4(), user_id=user.id, brand_id=brand_id,
                       message="has added new article", created_at=calendar.timegm(time.gmtime()), date=date.today())
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        config.logging.warning(
            f"Api - Post artical: Failed to submit data. {data['canonical_link']}")
        raise BadRequest(f"Failed to save data in database")
    return save_article


def url_validator(url, link_info):
    try:
        requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=28)
    except requests.exceptions.Timeout:
        raise BadRequest(f"This site is not supported by platform")
    except Exception as e:
        config.logging.warning(
            f"Url Validator: {link_info} URL is not reachable.")
        raise BadRequest(f"{link_info} URL is not reachable.")


def validations(data, brand_id):
    content_available = BrandContent.query.filter_by(
        canonical_link=data['canonical_link']).first()
    # if content_available:
    #     if str(content_available.brand_id) == brand_id:
    #         raise BadRequest("Article available in database.")

    # url_validator(data['canonical_link'], 'canonical link')
    save_ob = post_article(data, brand_id)
    return save_ob, HTTPStatus.CREATED.value


def get_all_articles(brand_id, search, page, limit):
    try:
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(
            f"Api: Get All Article : Invalid Submission Brand Id. {brand_id}")
        raise BadRequest("Brand id not valid.")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        raise BadRequest(
            f"Brand not found in database. Please check brand Id - {brand_id}.")
    if search:
        sear = "%{}%".format(search)
        articles = BrandContent.query.order_by(BrandContent.updated_at.desc()).filter(
            BrandContent.brand_id == brand_id).filter(or_(BrandContent.title.ilike(sear), BrandContent.description.ilike(sear), BrandContent.site_name.ilike(sear))).paginate(page=page, per_page=limit)
    else:
        articles = BrandContent.query.order_by(BrandContent.updated_at.desc()).filter(
            BrandContent.brand_id == brand_id).paginate(page=page, per_page=limit)
    total_page = [page for page in articles.iter_pages()]
    return {
        "items": articles.items,
        "total_pages": total_page if total_page else [],
        "has_next": articles.has_next,
        "has_prev": articles.has_prev,
        "page": articles.page,
        "per_page": articles.per_page,
        "total": articles.pages
    }, HTTPStatus.OK.value


def get_article(article_id):
    try:
        uuid.UUID(article_id)
    except Exception as e:
        config.logging.warning(
            f"api: Get article by id : Invalid submission article Id:- {article_id}")
        raise BadRequest(f"Invalid submission article Id:- {article_id}.")
    article = BrandContent.query.filter_by(id=article_id).first()
    if not article:
        raise BadRequest(
            "Article not available in database. Please check article id.")
    return article


def delete_article(article_id):
    try:
        uuid.UUID(article_id)
    except Exception as e:
        config.logging.warning(
            f"api: Delete Article : Invalid Submission Article Id. {article_id}")
        raise BadRequest("Article id is not valid.")
    article = BrandContent.query.filter_by(id=article_id).first()
    if not article:
        raise BadRequest(
            "Article not available in database. Please check article id.")
    try:
        db.session.delete(article)
        log = BrandLog(id=uuid.uuid4(), user_id=article.user_id, brand_id=article.brand_id,
                       message="has deleted one article", created_at=calendar.timegm(time.gmtime()), date=date.today())
        db.session.add(log)
        db.session.commit()
        return {
            "message": "Article Deleted Successfully.",
        }, HTTPStatus.OK.value
    except Exception as e:
        return {"message": f"Can't delete Article due to: {e}"}, HTTPStatus.OK.value


def update_article(data, article_id, brand_id):
    article = BrandContent.query.filter_by(id=article_id).first()
    if not article:
        raise BadRequest(
            "Article not available in database. Please check article id.")
    if "image_link" in data.keys():
        if "base64" in data["image_link"]:
            image_link = upload_image_by_raw(data["image_link"], brand_id)
        else:
            image_link = image_upload_by_url(data["image_link"], brand_id)
    try:
        article.title = data['title']
        article.description = data['description']
        article.canonical_link = data['canonical_link']
        article.image_link = image_link
        article.tags = data['tags']
        article.content_type = data['content_type']
        article.site_name = data["site_name"]
        article.favicon_icon_link = data['favicon_icon_link']
        article.updated_at = calendar.timegm(time.gmtime())
        log = BrandLog(id=uuid.uuid4(), user_id=article.user_id, brand_id=article.brand_id,
                       message="has updated one article", created_at=calendar.timegm(time.gmtime()), date=date.today())
        db.session.add(log)
        db.session.commit()
        return article, HTTPStatus.OK.value
    except Exception as e:
        config.logging.warning(
            f"api: update article: not able to update data: {data['canonical_link']}")
        raise BadRequest(
            f"Article not be updated please check Input. {data['canonical_link']}")
