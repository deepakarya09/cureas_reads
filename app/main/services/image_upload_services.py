import base64
from http import HTTPStatus
import io
import uuid
import requests
from app.main.models.brands import Brand
from google.cloud import storage
from werkzeug.exceptions import BadRequest
from app.main import db, config
from PIL import Image
from flask import current_app as cur_app
storage_client = storage.Client()


def upload_image_bucket_brand(bytes_im, brand_id):
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        raise BadRequest(
            "Brand not available in database. Please check again.")
    brand_fqdn = brand.fqdn
    file_name = str(uuid.uuid4()) + ".png"
    try:
        bucket = storage_client.get_bucket(cur_app.config["BUCKET_NAME"])
        thumbnail_blob = bucket.blob(
            f"{cur_app.config['REMOTE_IMAGE_PAGE_DIRECTORY']}{brand_fqdn}/" + file_name)
        thumbnail_blob.upload_from_string(bytes_im, content_type="image/png")
        return thumbnail_blob.public_url
    except Exception as e:
        config.logging.error(f"Error in upload image due to {e}")
        raise BadRequest(f"Error in upload image due to {e}")


def upload_image_by_raw(raw_image, brand_id):
    try:
        image_data = base64.b64decode(raw_image.split(",")[1])
        im_file = io.BytesIO(image_data)  # convert image to file-like object
        img = Image.open(im_file)
        # if img.size[0] > img.size[1]:
        #     w_percent = (config.img_base_width / float(img.size[0]))
        #     h_size = int((float(img.size[1]) * float(w_percent)))
        #     img = img.resize((config.img_base_width, h_size), Image.ANTIALIAS)
        # else:
        #     h_percent = (config.img_base_height / float(img.size[1]))
        #     w_size = int((float(img.size[0]) * float(h_percent)))
        #     img = img.resize((w_size, config.img_base_height), Image.ANTIALIAS)
        try:
            buf = io.BytesIO()
            img.save(buf, format="PNG", quality=100)
            bytes_im = buf.getvalue()
        except Exception as e:
            raise BadRequest(f"{e}")
    except Exception as e:
        raise BadRequest(f"Incorrect image format {e}")
    try:
        cdn_image_link = upload_image_bucket_brand(
            bytes_im=bytes_im, brand_id=brand_id)
        return cdn_image_link
    except Exception as e:
        raise BadRequest(f"Error in upload image due to {e}")
    
def upload_image_by_raw_social(raw_image, brand_id):
    try:
        image_data = base64.b64decode(raw_image.split(",")[1])
        im_file = io.BytesIO(image_data)  # convert image to file-like object
        img = Image.open(im_file)
        try:
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            bytes_im = buf.getvalue()
        except Exception as e:
            raise BadRequest(f"{e}")
    except Exception as e:
        raise BadRequest(f"Incorrect image format {e}")
    try:
        cdn_image_link = upload_image_bucket_brand(
            bytes_im=bytes_im, brand_id=brand_id)
        return cdn_image_link
    except Exception as e:
        raise BadRequest(f"Error in upload image due to {e}")


def image_upload_by_url(image_url, brand_id):
    try:
        img = Image.open(io.BytesIO(requests.get(image_url, headers={
            'User-Agent': 'Mozilla/5.0'}, timeout=28, stream=True).content))
    except Exception as e:
        config.logging.warning(f"Faild to load image{e}")
        raise BadRequest(f"Faild to load image {e}")
    # if img.size[0] > img.size[1]:
    #     w_percent = (config.img_base_width / float(img.size[0]))
    #     h_size = int((float(img.size[1]) * float(w_percent)))
    #     img = img.resize((config.img_base_width, h_size), Image.ANTIALIAS)
    # else:
    #     h_percent = (config.img_base_height / float(img.size[1]))
    #     w_size = int((float(img.size[0]) * float(h_percent)))
    #     img = img.resize((w_size, config.img_base_height), Image.ANTIALIAS)
    try:
        buf = io.BytesIO()
        img.save(buf, format="PNG", quality=100)
        bytes_im = buf.getvalue()
        cdn_image_link = upload_image_bucket_brand(
            bytes_im=bytes_im, brand_id=brand_id)
        return cdn_image_link
    except Exception as e:
        config.logging.warning(f"Faild to load image{e}")
        raise BadRequest(f"Faild to load image {e}")

def image_upload_by_url_social(image_url, brand_id):
    try:
        img = Image.open(io.BytesIO(requests.get(image_url, headers={
            'User-Agent': 'Mozilla/5.0'}, timeout=28, stream=True).content))
    except Exception as e:
        config.logging.warning(f"Faild to load image{e}")
        raise BadRequest(f"Faild to load image {e}")
    try:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        bytes_im = buf.getvalue()
        cdn_image_link = upload_image_bucket_brand(
            bytes_im=bytes_im, brand_id=brand_id)
        return cdn_image_link
    except Exception as e:
        config.logging.warning(f"Faild to load image{e}")
        raise BadRequest(f"Faild to load image {e}")


def upload_images_api(brand_id, data):
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        raise BadRequest("Brand Not Found")
    if "base64" in data["image"]:
        image_link = upload_image_by_raw(data["image"], brand_id)
        return {"image_link": image_link}
    else:
        image_link = image_upload_by_url(data["image"], brand_id)
        return {"image_link": image_link}

def upload_images_api_social(brand_id, data):
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        raise BadRequest("Brand Not Found")
    if "base64" in data["image"]:
        image_link = upload_image_by_raw_social(data["image"], brand_id)
        return {"image_link": image_link}
    else:
        image_link = image_upload_by_url_social(data["image"], brand_id)
        return {"image_link": image_link}


def image_byte(data):
    try:
        img = Image.open(io.BytesIO(requests.get(data['link'], headers={
            'User-Agent': 'Mozilla/5.0'}, timeout=28, stream=True).content))
    except Exception as e:
        config.logging.warning(
            f"Faild to load image please check image url{e}")
        raise BadRequest(f"Faild to load image please check image url {e}")
    try:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        bytes_im = buf.getvalue()
        image = base64.b64encode(bytes_im)
        image_data = image.decode('UTF-8')
        return {"data": "data:image/png;base64,"+image_data}
    except Exception as e:
        config.logging.warning(f"Faild to encode image,Please try again {e}")
        raise BadRequest(f"Faild to encode image, Please try again{e}")
