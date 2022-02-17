from http import HTTPStatus
import re
import uuid
from werkzeug import exceptions
from werkzeug.exceptions import BadRequest
from app.main.models.brands import Brand
from app.main.models.branding_pages import BrandPages
from app.main.models.page_seo import PageSeo
from app.main.services.image_upload_services import upload_images_api
from app.main import config, db
from app.main.services import get_time


def save_page_seo(page_id, data):
    page = BrandPages.query.filter_by(id=page_id).first()
    if not page:
        raise BadRequest("This page id is not in database")
    seo = PageSeo.query.filter_by(page_id=page_id).first()
    if seo:
        raise BadRequest("This page have already seo please update data")
    brand_id = page.brand_id
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        raise BadRequest("This page is not connected with any brand")
    if "banner_image" in data:
        post = {"image": data["banner_image"]}
        banner_link = upload_images_api(brand_id, post)
        if not banner_link:
            banner_link = "#"
    if page.cdn_html_page_link == None:
        page_lin = "#"
    else:
        page_lin = page.cdn_html_page_link
    try:
        save = PageSeo(id=uuid.uuid4(), page_id=page.id, banner_image=banner_link["image_link"],
                       icon=brand.white_theme_logo if brand.white_theme_logo else "#", title=data["title"], description=data["description"], page_link=page_lin, page_type=data["page_type"], facebook_publisher=data["facebook_publisher"], twitter_id=data["twitter_id"])

        db.session.add(save)
        db.session.commit()
        return save, HTTPStatus.CREATED

    except Exception as e:
        raise BadRequest("Error in saving seo of page")


def update_page_seo(page_id, data):
    page = BrandPages.query.filter_by(id=page_id).first()
    if not page:
        raise BadRequest("This page id is not in database")
    seo = PageSeo.query.filter_by(page_id=page_id).first()
    if not seo:
        raise BadRequest("This page not have seo please create first")
    brand_id = page.brand_id
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        raise BadRequest("This page is not connected with any brand")
    if "banner_image" in data:
        post = {"image": data["banner_image"]}
        banner_link = upload_images_api(brand_id, post)
        setattr(seo, "banner_image", banner_link["image_link"])
    try:
        for key, value in data.items():
            if key == "banner_image":
                pass
            elif getattr(seo, key) != value:
                setattr(seo, key, value)
        setattr(seo, "updated_at", get_time())
    except Exception as e:
        config.logging.critical(f"Failed to updated seo:{e}")
        raise BadRequest("Seo Update Failed")
    db.session.commit()
    return seo, HTTPStatus.OK


def get_page_seo(page_id):
    try:
        uuid.UUID(page_id)
    except Exception as e:
        config.logging.warning(
            f"api: get brand id : Invalid submission page Id. {page_id}")
        raise BadRequest(f"This paeg id not valid.")
    try:
        page = BrandPages.query.filter_by(id=page_id).first()
        if not page:
            raise BadRequest("This page id is not in database")
        seo = PageSeo.query.filter_by(page_id=page_id).first()
        if not seo:
            raise BadRequest("This page not have data")
        return seo, HTTPStatus.OK
    except Exception as e:
        config.logging.critical(f"Failed to get seo:{e}")
        raise BadRequest("Failed to get Seo data")
