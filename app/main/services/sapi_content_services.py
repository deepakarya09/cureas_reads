import calendar
import io
import time
import uuid
from http import HTTPStatus

import requests
from PIL import Image
from sqlalchemy import or_
from werkzeug.exceptions import BadRequest

from app.main import config
from app.main import db
from flask import current_app as cur_app
from app.main.gcp_clients.bucket import upload_bucket
from app.main.models.contents import Content
from app.main.models.tags import Tag
from app.main.services.tags_service import post_tag


def image_gen(image_url):
    try:
        img = Image.open(io.BytesIO(requests.get(image_url, headers={
            'User-Agent': 'Mozilla/5.0'}, timeout=28, stream=True).content))
    except Exception as e:
        config.logging.warning(f"Faild to load image{e}")
        raise BadRequest("Faild to load image")

    file = str(uuid.uuid4()) + ".png"
    if img.size[0] > img.size[1]:
        w_percent = (config.img_base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((config.img_base_width, h_size), Image.ANTIALIAS)
    else:
        h_percent = (config.img_base_height / float(img.size[1]))
        w_size = int((float(img.size[0]) * float(h_percent)))
        img = img.resize((w_size, config.img_base_height), Image.ANTIALIAS)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    bytes_im = buf.getvalue()

    upload_bucket(bytes_im=bytes_im, remote_path=cur_app.config["REMOTE_IMAGE_PAGE_DIRECTORY"] + file)

    cdn_image_link = cur_app.config["BUCKET_BASE_URL"] + cur_app.config["REMOTE_IMAGE_PAGE_DIRECTORY"] + file
    return cdn_image_link


def temp_save_content(data, tag_objects):
    if Content.query.filter_by(canonical_link=data['canonical_link']).first():
        config.logging.warning(f"This site link already present. from submission article {data['canonical_link']}")
        return

    try:
        save_con = Content(
            id=uuid.uuid4(),
            title=data['title'],
            description=data['description'],
            site_link=data['site_link'],
            canonical_link=data['canonical_link'],
            image_link=data['image_link'],
            cdn_image_link=image_gen(data['image_link']),
            content_type_id=data['content_type'] if (
                    "content_type" in data and len(data['content_type']) == 36) else None,
            source_id=data['source_id'] if ("source_id" in data and len(
                data['source_id']) == 36) in data else None,
            type=data['type'],
            country=data['country'] if "country" in data else cur_app.config['DEFAULT_COUNTRY'],
            site_name=data["site_name"],
            created_at=calendar.timegm(time.gmtime()),
            modified_at=calendar.timegm(time.gmtime())
        )
    except Exception:
        config.logging.warning(f"content: Failed to submit data. {data['canonical_link']}")
        return

    for tag in tag_objects:
        save_con.tag.append(tag)
    db.session.add(save_con)
    db.session.commit()
    return save_con


def save_content(data, tag_objects):
    try:
        save_con = Content(
            id=uuid.uuid4(),
            title=data['title'],
            description=data['description'],
            site_link=data['site_link'],
            canonical_link=data['canonical_link'],
            image_link=data['image_link'],
            cdn_image_link=image_gen(data['image_link']),
            content_type_id=data['content_type'] if (
                    "content_type" in data and len(data['content_type']) == 36) else None,
            source_id=data['source_id'] if ("source_id" in data and len(
                data['source_id']) == 36) in data else None,
            type=data['type'],
            country=data['country'] if "country" in data else cur_app.config['DEFAULT_COUNTRY'],
            site_name=data["site_name"],
            created_at=calendar.timegm(time.gmtime()),
            modified_at=calendar.timegm(time.gmtime())
        )
    except Exception as e:
        config.logging.critical(f"Failed to submit data in save content with exception {e}")
        raise BadRequest("content: Failed to submit data.")

    for tag in tag_objects:
        save_con.tag.append(tag)
    db.session.add(save_con)
    db.session.commit()
    return save_con


def url_validator(url, link_info):
    try:
        requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=28)
    except requests.exceptions.Timeout:
        raise BadRequest(f"This site is not supported by platform")
    except Exception as e:
        raise BadRequest(f"{link_info} URL is not reachable.")


def validation(data):
    if Content.query.filter_by(canonical_link=data['canonical_link']).first():
        raise BadRequest("This site link already present.")

    url_validator(data['canonical_link'], 'canonical link')
    url_validator(data['site_link'], 'site link')

    tag_objects = []
    try:
        for tag in data['tags']:
            tag_ob = Tag.query.filter_by(name=tag.lower()).first()
            if not tag_ob:
                tag_ob = post_tag(tag)
            tag_objects.append(tag_ob)
    except Exception as e:
        config.logging.critical(f"Failed to save with exception {e}")
        raise BadRequest("Tag field not in input.")

    save_ob = save_content(data, tag_objects)
    return save_ob, HTTPStatus.CREATED.value


def get_all_contents(page, limit, searchKey):
    if searchKey:
        search = "%{}%".format(searchKey)
        paginated_data = Content.query.order_by(
            Content.created_at.desc()).filter(or_(Content.title.ilike(search), Content.description.ilike(search),
                                                  Content.country.ilike(search))).paginate(page=page, per_page=limit)
        objects = paginated_data.items
    else:
        paginated_data = Content.query.order_by(
            Content.created_at.desc()).paginate(page=page, per_page=limit)
        objects = paginated_data.items

    return {"items": objects,
            "total_pages": [page for page in paginated_data.iter_pages()],
            "page": paginated_data.page,
            "per_page": paginated_data.per_page,
            "total": paginated_data.total,
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


def update_content(id, data):
    try:
        id = uuid.UUID(id)
    except Exception as e:
        raise BadRequest("Not a valid ID")

    try:
        content = Content.query.filter_by(id=id).first()
        if not content:
            raise BadRequest("Content does not exists.")

        tag_objects = []
        payload_tags = list(map(lambda obj: str(obj).lower(), data['tags']))
        db_tags = list(map(lambda obj: obj, content.con_conn))
        bg_tag_val = [tag.name for tag in db_tags]
        payload_tags.sort()
        bg_tag_val.sort()

        if payload_tags != bg_tag_val:
            content.con_conn = []

            try:
                for tag in data['tags']:
                    tag_ob = Tag.query.filter_by(name=tag.lower()).first()
                    if not tag_ob:
                        tag_ob = post_tag(tag)
                    tag_objects.append(tag_ob)
            except Exception as e:
                config.logging.warning(f"sapi content tag: Tag field not in input.{e}")
                raise BadRequest("Tag field not in input.")
        try:
            payload_data = data.copy()
            del payload_data["tags"]

            content.updated_at = calendar.timegm(time.gmtime())
            if content.image_link != payload_data["image_link"]:
                try:
                    content.cdn_image_link = image_gen(data['image_link'])
                    content.image_link = payload_data["image_link"]
                    del payload_data["image_link"]
                except Exception as e:
                    config.logging.warning(f"Image link: Not Valid:{e}")
                    raise BadRequest("Image link: Not Valid")
            else:
                del payload_data["image_link"]
            for key, value in payload_data.items():
                try:
                    if hasattr(content, key):
                        col_val = getattr(content, key)
                        if col_val != value:
                            setattr(content, key, value)
                    else:
                        config.logging.warning(
                            "Payload key not match with the column name in db")
                        raise BadRequest("failed to Update")
                except AttributeError:
                    config.logging.warning("AttributeError")
                    raise BadRequest("AttributeError")

        except Exception as e:
            config.logging.warning(f"content: Failed to submit data:{e}")
            raise BadRequest("content: Failed to submit data.")
    except Exception as e:
        config.logging.warning(f"content: Failed to submit data:{e}")
        raise BadRequest("content: Failed to submit data.")
    try:
        for tag in tag_objects:
            content.tag.append(tag)
        db.session.commit()
    except Exception as e:
        config.logging.warning(f"Error to submit data:{e}")
        raise BadRequest(f"Content: Failed to submit data.")
    return content, HTTPStatus.CREATED.value
