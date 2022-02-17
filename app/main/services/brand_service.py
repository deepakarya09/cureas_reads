from app.main.models.brand_log import BrandLog
from app.main.models.page_component import PageComponent
from app.main.models.membership import Membership
from app.main.models.rolebranduser import RoleBrandUser
from app.main.services import get_active_user, get_time
from app.main.models.branding_pages import BrandPages
import base64
import calendar
import json
from sqlalchemy import or_
import time
from flask import current_app as cur_app
import uuid
from http import HTTPStatus
import requests
from werkzeug.exceptions import BadRequest
from app.main import db, config
from app.main.gcp_clients.bucket import upload_bucket
from app.main.models.brands import Brand
from app.main.models.user import User
from app.main.config import ssl_logger
from app.main.services.ssl_generation_services import create_ssl
import threading
from datetime import date


def get_int_date(): return calendar.timegm(time.gmtime())


def upload_logo(image_data, file):
    try:
        image_data = base64.b64decode(image_data.split(",")[1])
    except Exception as e:
        raise BadRequest(f"Incorrect image format {e}")
    try:
        upload_bucket(bytes_im=image_data,
                      remote_path=cur_app.config["LOGO"] + file)
        cdn_image_link = cur_app.config["BUCKET_BASE_URL"] + \
            cur_app.config["LOGO"] + file
        return cdn_image_link
    except Exception as e:
        raise BadRequest(f"Error in upload image{e}")


def get_brand_from_user(user_id):
    try:
        uuid.UUID(user_id)
    except Exception as e:
        config.logging.warning(
            f"api: get brand by user id : Invalid Submission Id. {e}")
        raise BadRequest("Not valid user id please check ID.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise BadRequest("User not found in database. Please check user id.")
    brands = Brand.query.join(Membership).filter(
        Membership.user_id == user.id).order_by(Brand.created_at.desc()).all()
    items = []
    if brands:
        for i in brands:
            role = RoleBrandUser.query.join(Membership).filter(
                Membership.brand_id == i.id).filter(Membership.user_id == user.id).first()
            active = Membership.query.filter(
                Membership.brand_id == i.id, Membership.user_id == user.id).first()
            data = {
                "id": i.id,
                "user_role": role.name,
                "user_id": i.user_id,
                "name": i.name,
                "site_url": i.site_url,
                "description": i.description,
                "facebook_url": i.facebook_url,
                "twitter_url": i.twitter_url,
                "instagram_url": i.instagram_url,
                "created_at": i.created_at,
                "updated_at": i.updated_at,
                "white_theme_logo": i.white_theme_logo,
                "black_theme_logo": i.black_theme_logo,
                "colors": i.colors,
                "fonts": i.fonts,
                "light_theme": i.light_theme,
                "seo_description": i.seo_description,
                "seo_title": i.seo_title,
                "favicon_img": i.favicon_img,
                "terms_condition": i.terms_condition,
                "privacy_policy": i.privacy_policy,
                "font_size": i.font_size,
                "active": active.active,
                "email_api_key": i.email_api_key
            }
            items.append(data)
    return {"items": items}


def get_users_from_brand(brand_id):
    try:
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(
            f"api: get brand by brand id : Invalid Submission Id. {e}")
        raise BadRequest("Not a valid brand id please check ID.")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        raise BadRequest("Brand not found in database. Please check brand id.")
    data = Membership.query.filter(
        Membership.brand_id == brand.id).order_by(Membership.created_at.desc()).all()
    users = []
    for i in data:
        user = User.query.filter(User.id == i.user_id).first()
        role = RoleBrandUser.query.filter(
            RoleBrandUser.id == i.role_id).first()
        d = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "image_url": user.image_url,
            "role": user.role,
            "verified": user.verified,
            "login_type": user.login_type,
            "first_brand_exists": user.first_brand_exists,
            "brand_role": [{"id": role.id, "role": role.name}]
        }
        users.append(d)
    return {"items": users}


def is_valid_id(brand_id, id):
    try:
        brand_id = uuid.UUID(brand_id)
    except Exception:
        raise BadRequest(f"Incorrect {id} ID!")
    return brand_id


def post_brand(data):
    if "brand_id" not in data:
        if Brand.query.filter_by(site_url=data['site_url']).first() and data['site_url'] is not None:
            raise BadRequest(
                f"{data['site_url']} already exists in database. Please use different link.")
        if Brand.query.filter_by(name=data['name']).first():
            raise BadRequest(
                f"{data['name']} brand name is already available in database. Please use different name.")
        user = User.query.filter_by(id=data['user_id']).first()
        if not user:
            raise BadRequest(
                "User not found. Please create account or try to re-login")

        webname = (data['name'].replace(" ", "")).lower()
        role = RoleBrandUser.query.filter_by(name="Owner").first()
        if not role:
            raise BadRequest("Database have not any role with name Owner.")
        navbar = PageComponent.query.filter(PageComponent.category == "navbar").filter(
            PageComponent.active == True).first()
        if not navbar:
            raise BadRequest("not have any active navbar in componnent")
        footer = PageComponent.query.filter(PageComponent.category == "footer").filter(
            PageComponent.active == True).first()
        if not footer:
            raise BadRequest("not have any active footer in componnent")
        try:
            brand = Brand(id=uuid.uuid4(), name=data["name"], user_id=data["user_id"],
                          site_url=data["site_url"],
                          fqdn=str(webname)+cur_app.config["DOMAIN_NAME"],
                          default_fqdn=str(webname) +
                          cur_app.config["DOMAIN_NAME"],
                          description=data["description"],
                          facebook_url=data["facebook_url"], twitter_url=data["twitter_url"],
                          instagram_url=data["instagram_url"], created_at=get_int_date(
            ),
                updated_at=get_int_date(),
                footer_html=footer.data, navbar_html=navbar.data, footer_id=footer.id, navbar_id=navbar.id)
            db.session.add(brand)
            db.session.commit()
        except Exception as e:
            config.logging.critical(f"Post brand failed with exception {e}")
            raise BadRequest(
                "Failed to create new brand please check filled data again.")
        try:
            new_brand = Brand.query.filter_by(id=brand.id).first()
            if not new_brand:
                raise BadRequest("Brand is not created please create again")
            connect = Membership(
                user_id=user.id,
                brand_id=new_brand.id,
                role_id=role.id
            )
        except Exception as e:
            config.logging.critical(f"Failed to assign brand to user {e}")
            raise BadRequest(
                "Failed to assign brand to logged in user. Please login again or create brand.")
        db.session.add(connect)
        db.session.commit()
        return brand, HTTPStatus.CREATED

    data['id'] = data['brand_id']
    del data["brand_id"]
    brand = Brand.query.filter_by(id=data['id']).first()

    if not brand:
        raise BadRequest("Brand not found. Please check brand id!")

    for key in data.keys():
        if getattr(brand, key) != data[key]:
            setattr(brand, key, data[key])
    db.session.commit()
    return brand, HTTPStatus.OK


def get_brand_details(brand_id):
    brand = Brand.query.filter_by(id=is_valid_id(brand_id, "brand")).first()
    if not brand:
        raise BadRequest("Brand not found. Please check brand id!")
    return brand, HTTPStatus.OK


def post_brand_style(brand_id, data):
    brand = Brand.query.filter_by(id=is_valid_id(brand_id, "brand"), ).first()

    if not User.query.filter_by(id=data['user_id']).first():
        raise BadRequest("User not found. Please check user id")
    if not brand:
        raise BadRequest("Brand not found! Please check brand id")
    try:
        for key in data.keys():
            if getattr(brand, key) != data[key]:
                if (key == "white_theme_logo" and data["white_theme_logo"] != "") or (
                        key == "black_theme_logo" and data["black_theme_logo"] != ""):
                    setattr(brand, key, upload_logo(
                        data[key], str(uuid.uuid4()) + ".png"))
                elif key != "white_theme_logo" or key != "black_theme_logo":
                    setattr(brand, key, data[key])
                else:
                    pass

    except Exception as e:
        config.logging.critical(f"brand update failed with exception {e}")
        raise BadRequest(f"Failed to update due to {e}")
    try:
        user = User.query.filter_by(id=data["user_id"]).first()
        user.first_brand_exists = True
        log = BrandLog(id=uuid.uuid4(), user_id=brand.user_id, brand_id=brand_id,
                       message="Welcome in new Brand", created_at=get_time(), date=date.today())
        db.session.add(log)
    except Exception as e:
        config.logging.critical(f"brand update failed with exception {e}")
        raise BadRequest("Failed to update user first brand exists flag")

    db.session.commit()
    try:
        fqdn = f"https://{brand.fqdn}/"
        domain_name = {"site_url": fqdn}
        from manage import app
        with app.app_context():
            threading.Thread(target=create_ssl, args=(domain_name,)).start()
        # create_ssl(data=domain_name)
    except Exception as e:
        ssl_logger.exception(
            f'exeption while creating ssl at brand create time - {fqdn} ')
    return brand, HTTPStatus.OK


def google_font():
    return [{"family": font['family'], 'category': font['category']} for font in json.loads(requests.get(
            "https://www.googleapis.com/webfonts/v1/webfonts?key=AIzaSyDlaHOQoHaXZEs1jHgWClrkvDgfoBPFmJY").content)['items']]


def get_all_brands(page, limit, searchKey, category):
    if searchKey:
        search = "%{}%".format(searchKey)
        subquery = BrandPages.query(BrandPages.brand_id).filter(
            BrandPages.status == "PUBLISHED", BrandPages.cdn_html_page_link != '').subquery()
        paginate_brands = db.session.query(Brand).filter(
            Brand.id.in_(subquery)).filter(or_(Brand.name.ilike(search))).order_by(Brand.created_at.desc()).paginate(page=page, per_page=limit)
    elif category:
        subquery = db.session.query(BrandPages.brand_id).filter(
            BrandPages.status == "PUBLISHED", BrandPages.cdn_html_page_link != '', BrandPages.category == category).subquery()

        paginate_brands = db.session.query(Brand).filter(
            Brand.id.in_(subquery)).order_by(Brand.created_at.desc()).paginate(page=page, per_page=limit)
    else:

        subquery = db.session.query(BrandPages.brand_id).filter(
            BrandPages.status == "PUBLISHED").subquery()

        paginate_brands = db.session.query(Brand).filter(Brand.id.in_(subquery)).order_by(
            Brand.created_at.desc()).paginate(page=page, per_page=limit)

        # paginate_brands = Brand.query.order_by(
        # Brand.created_at.desc()).filter(BrandPages.brand_id.in_(subquery)).paginate(page=page, per_page=limit)
    # if not paginate_brands:
    #     raise BadRequest("Brand not available")
    # obj = []
    # for i in paginate_brands.items:
    #     firstpage = BrandPages.query.order_by(BrandPages.created_at.desc()).filter(
    #         BrandPages.brand_id == i.id, BrandPages.status == "PUBLISHED").first()
    #     id = i.id
    #     name = i.name
    #     link = "https://" + i.fqdn
    #     if firstpage and firstpage.cdn_html_page_link:
    #         data = {"id": str(id), "name": name, "fqdn": link,
    #                 "firstpage": firstpage.cdn_html_page_link if firstpage else None}

    #         obj.append(data)

    return {
        "items": paginate_brands.items,
        "total_pages": [page for page in paginate_brands.iter_pages()],
        "page": paginate_brands.page,
        "has_next": paginate_brands.has_next,
        "has_prev": paginate_brands.has_prev,
        "per_page": paginate_brands.per_page,
        "total": paginate_brands.total
    }, HTTPStatus.OK.value


def update_brand(brand_id, data):
    brand = Brand.query.filter_by(id=is_valid_id(brand_id, "brand"), ).first()
    if not brand:
        raise BadRequest("Brand not found in database. Please check brand id.")
    try:
        for key in data.keys():
            if getattr(brand, key) != data[key]:
                if (key == "white_theme_logo" and data["white_theme_logo"] != "") or (
                        key == "black_theme_logo" and data["black_theme_logo"] != "") or (key == "favicon_img" and data["favicon_img"] != ""):
                    setattr(brand, key, upload_logo(
                        data[key], str(uuid.uuid4()) + ".png"))
                elif key != "white_theme_logo" or key != "black_theme_logo" or key != "favicon_img":
                    setattr(brand, key, data[key])
                else:
                    pass
        setattr(brand, "updated_at", get_time())
        log = BrandLog(id=uuid.uuid4(), user_id=brand.user_id, brand_id=brand_id,
                       message=f"{brand.name} has been updated", created_at=get_time(), date=date.today())
        db.session.add(log)
    except Exception as e:
        config.logging.critical(f"Failed to updated widget:{e}")
        raise BadRequest("Error in updating brand. Please check given data.")
    db.session.commit()
    return brand, HTTPStatus.OK


def set_brand_active(brand_id):
    i = Brand.query.filter_by(id=is_valid_id(brand_id, "brand")).first()
    if not i:
        raise BadRequest("Brand not found in database. Please check brand id.")
    try:
        set_inactive = Membership.query.filter(
            Membership.user_id == get_active_user(), Membership.active == True).first()
        if set_inactive:
            set_inactive.active = False
            db.session.commit()
    except Exception as e:
        config.logging.critical(f"Failed to set inactive brand:{e}")
        raise BadRequest(
            "Error in making brand inactive. Please check brand id and login account.")

    try:
        set_active = Membership.query.filter(
            Membership.brand_id == brand_id, Membership.user_id == get_active_user()).first()
        if not set_active:
            raise BadRequest(
                "Please check that you are login with correct account, you are not assigned with this brand")
        set_active.active = True
        db.session.commit()
    except Exception as e:
        config.logging.critical(f"Failed to set active brand:{e}")
        raise BadRequest(
            "Error in making brand active. Please check brand id and login account.")
    role = RoleBrandUser.query.join(Membership).filter(
        Membership.brand_id == i.id).filter(Membership.user_id == get_active_user()).first()
    return {
        "id": i.id,
        "user_role": role.name,
        "user_id": i.user_id,
        "name": i.name,
        "site_url": i.site_url,
        "description": i.description,
        "facebook_url": i.facebook_url,
        "twitter_url": i.twitter_url,
        "instagram_url": i.instagram_url,
        "created_at": i.created_at,
        "updated_at": i.updated_at,
        "white_theme_logo": i.white_theme_logo,
        "black_theme_logo": i.black_theme_logo,
        "colors": i.colors,
        "fonts": i.fonts,
        "light_theme": i.light_theme,
        "seo_description": i.seo_description,
        "seo_title": i.seo_title,
        "favicon_img": i.favicon_img,
        "terms_condition": i.terms_condition,
        "privacy_policy": i.privacy_policy,
        "font_size": i.font_size,
        "active": set_active.active,
        "email_api_key": i.email_api_key
    }


def remove_user_from_brand(user_id, brand_id):
    try:
        uuid.UUID(brand_id)
        uuid.UUID(user_id)
    except Exception as e:
        config.logging.warning(
            f"api: get brand by brand id : Invalid Submission Id. {e}")
        raise BadRequest("Not a valid brand id please check ID.")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        raise BadRequest("Brand not found in database. Please check brand id.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise BadRequest("User not found in database. Please check user id.")
    active_user = get_active_user()
    if str(brand.user_id) != str(active_user):
        raise BadRequest(
            "You are not authorized to remove user from this brand")
    if str(brand.user_id) == str(user_id):
        raise BadRequest("You can't remove owner from brand")
    if str(user_id) == str(active_user):
        raise BadRequest("You are active user you can't remove your self")
    try:
        check = Membership.query.filter(
            Membership.brand_id == brand_id, Membership.user_id == user_id).first()
        if not check:
            raise BadRequest(
                "This user is not assigned to this brand in database")
        log = BrandLog(id=uuid.uuid4(), user_id=get_active_user(), brand_id=brand_id,
                       message=f"{user.email} has been removed", created_at=get_time(), date=date.today())
        db.session.add(log)
        db.session.delete(check)
        db.session.commit()
        return {"message": "User successfully removed from this brand"}, HTTPStatus.OK
    except Exception as e:
        config.logging.critical(f"Failed to remove user from brand:{e}")
        raise BadRequest(
            "Failed to remove user from brand.")


def change_role_of_brand_user(user_id, brand_id, role_id):
    try:
        uuid.UUID(brand_id)
        uuid.UUID(user_id)
        uuid.UUID(role_id)
    except Exception as e:
        config.logging.warning(
            f"api: change role of user : Invalid Submission Id. {e}")
        raise BadRequest("Not a valid id please check ID.")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        raise BadRequest("Brand not found in database. Please check brand id.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise BadRequest("User not found in database. Please check user id.")
    role = RoleBrandUser.query.filter_by(id=role_id).first()
    if not role:
        raise BadRequest("Role not found in database. Please check role id.")
    active_user = get_active_user()
    if str(brand.user_id) != str(active_user):
        raise BadRequest("You are not authorized to change role of accounts")
    if role.name == "Owner":
        raise BadRequest("You cannot assign Owner role to any other user")
    try:
        check = Membership.query.filter(
            Membership.brand_id == brand_id, Membership.user_id == user_id).first()
        if not check:
            raise BadRequest(
                "This user is not assigned to this brand in database")

        check.role_id = role.id
        log = BrandLog(id=uuid.uuid4(), user_id=get_active_user(), brand_id=brand_id,
                       message=f"{user.email} role changed to {role.name}", created_at=get_time(), date=date.today())
        db.session.add(log)
        db.session.commit()
        return {"message": "User role successfully changed"}, HTTPStatus.OK
    except Exception as e:
        config.logging.critical(f"Failed to remove user from brand:{e}")
        raise BadRequest(
            "Failed to remove user from brand.")
