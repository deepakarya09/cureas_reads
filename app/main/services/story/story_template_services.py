import base64
from app.main.gcp_clients.bucket import upload_bucket
from http import HTTPStatus
import calendar
import time
import uuid
from flask import current_app as cur_app
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import NotFound

from app.main import db, config
from app.main.models.story_template import StoryTemplate
from app.main.services import get_time


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
        raise BadRequest(f"Not able to upload image{e}")


def post_story_template(_temp):
    _tem = _temp['name']
    tem = StoryTemplate.query.filter_by(name=_tem).first()
    try:
        thumbnail_link = upload_thumbnail(
            _temp['thumbnail'], str(uuid.uuid4()) + ".png")
    except Exception as e:
        raise BadRequest(
            f"Not able to upload thubnail. Please check thumbnail input {e}")
    if tem:
        raise BadRequest("Template name already exist.")
    if _temp['block_count'] != len(_temp['block_structure']):
        raise BadRequest("Block count is not equal to block structure.")
    else:
        try:
            template = StoryTemplate(
                name=_temp['name'],
                raw_html=_temp['raw_html'],
                block_count=_temp['block_count'],
                block_structure=_temp['block_structure'],
                thumbnail=thumbnail_link,
                draft_css=_temp['draft_css'],
                publish_css=_temp['publish_css'],
                category=_temp['category'],
                social_support=_temp['social_support'],
                id=uuid.uuid4(),
                created_at=calendar.timegm(time.gmtime()),
                updated_at=calendar.timegm(time.gmtime())
            )
        except Exception as e:
            config.logging.warning(f"Data saving failed {e}")
            raise BadRequest(f"Data loading failed {e}")
        db.session.add(template)
        db.session.commit()
    return template, HTTPStatus.CREATED.value


def update_story_template(id, data):
    temp_var = StoryTemplate.query.filter_by(id=id).first()
    if not temp_var:
        raise BadRequest(
            "Error please check story template Id, Template not found in data:")
    if 'thumbnail' in data:
        try:
            thumbnail_link = upload_thumbnail(
                data['thumbnail'], str(uuid.uuid4()) + ".png")
            setattr(temp_var, "thumbnail", thumbnail_link)
        except Exception as e:
            raise BadRequest(f"Error please check thumbnail input {e}")
    try:
        for key, value in data.items():
            if key == "thumbnail":
                pass
            elif getattr(temp_var, key) != value:
                setattr(temp_var, key, value)
        setattr(temp_var, "updated_at", get_time())
    except Exception as e:
        config.logging.critical(f"Failed to updated story template:{e}")
        raise BadRequest("Update Failed")
    db.session.commit()
    return temp_var, HTTPStatus.OK.value


def get_all_story_template(category, page, limit):
    if category:
        if not (category == "General" or category == "Privacy" or category == "Terms" or category == "Home" or category == "Story"):
            config.logging.warning(
                f"api: get all widgit: please enter valid status!")
            raise BadRequest(
                "please enter valid key, General , Privacy , Terms, Home or Story!")

    mm = StoryTemplate.query.filter()
    if category:
        mm = mm.filter(StoryTemplate.category == category)
    item = mm.order_by(StoryTemplate.created_at.desc())

    paginated_data = item.paginate(page=page, per_page=limit)
    total_page = [page for page in paginated_data.iter_pages()]
    if not item:
        return {"items": []}, HTTPStatus.OK.value
    try:
        return {"items": paginated_data.items,
                "total_pages": total_page if total_page else [],
                "pages": paginated_data.pages,
                "has_next": paginated_data.has_next,
                "has_prev": paginated_data.has_prev,
                "page": paginated_data.page,
                "per_page": paginated_data.per_page,
                "total": paginated_data.total,
                }, HTTPStatus.OK.value
    except Exception as e:
        config.logging.critical(f"Failed to get story templates:{e}")
        raise BadRequest("Failed to get all story Templates")


def get_story_template_by_id(id):
    try:
        temp = StoryTemplate.query.filter_by(id=id).first()
        return temp, HTTPStatus.OK.value
    except:
        return {"message": "Template dose not exists."}, HTTPStatus.ok.value


def delete_story_template(id):
    try:
        content = StoryTemplate.query.filter_by(id=id).first()
        db.session.delete(content)
        db.session.commit()
        return {
            "message": "story template deleted successfully.",
        }, HTTPStatus.OK.value
    except:
        return {"message": "story template does not exists."}, HTTPStatus.OK.value
