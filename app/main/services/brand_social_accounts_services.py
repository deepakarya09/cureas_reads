from app.main import config, db
import uuid
import calendar
import time
import uuid
from http import HTTPStatus
from werkzeug.exceptions import BadRequest
from app.main.models.brand_log import BrandLog
from app.main.models.brand_social_accounts import BrandSocialAccounts
from app.main.models.brands import Brand
from app.main.models.membership import Membership
from app.main.models.social_access import SocialAccess
from app.main.services import get_active_user, get_time
import requests
from flask import current_app as cur_app
from app.main.models.user import User
from app.main.utils.api_brand_social_account_dto import SocialAccountsDto
from datetime import date


def get_all_social_accounts(brand_id, name):
    try:
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(f"api: get brand id not valid. {e}")
        raise BadRequest("get brand id not valid.")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        config.logging.warning(
            f"api: brand social account services: Brand not available!")
        raise BadRequest("Brand not available!")
    if name:
        if not (name == "Instagram" or name == "Facebook" or name == "Twitter" or name == "Linkedin"):
            config.logging.warning(
                f"api: brand social account services: please enter valid name!")
            raise BadRequest("Please enter valid name!")
    try:
        mm = BrandSocialAccounts.query.filter(
            BrandSocialAccounts.brand_id == brand_id, BrandSocialAccounts.active == True)
        if name:
            mm = mm.filter(BrandSocialAccounts.name == name)
        items = mm.order_by(BrandSocialAccounts.updated_at.desc())
        return {"items": items}, HTTPStatus.OK.value
    except Exception as e:
        config.logging.critical(f"Failed to get social Instagram account:{e}")
        raise BadRequest(
            "Error in getting all Social Instagram Account.")


def create_social_account_instagram(brand_id, data):
    try:
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(f"api: get brand id not valid. {e}")
        raise BadRequest("get brand id not valid.")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        config.logging.warning(
            f"api: brand social account services: Brand not available!")
        raise BadRequest("Brand not available!")
    user_id = get_active_user()
    if str(brand.user_id) != str(user_id):
        raise BadRequest("You are not authorized to add social accounts")
    if "access_token" not in data:
        raise BadRequest("please add access_token in data")
    try:
        client_id = cur_app.config["FB_CLIENT_ID"]
        client_secret = cur_app.config["FB_CLIENT_SECRET"]
        access = requests.get(
            f"https://graph.facebook.com/v12.0/oauth/access_token?grant_type=fb_exchange_token&client_id={client_id}&client_secret={client_secret}&fb_exchange_token={data['access_token']}")
        access_token = access.json()["access_token"]
        fb_pages = requests.get(
            f"https://graph.facebook.com/v12.0/me/accounts?access_token={access_token}")
        fb_pages_id = []
        if "data" in fb_pages.json():
            for i in fb_pages.json()['data']:
                fb_pages_id.append(i['id'])
        else:
            raise BadRequest("pages not in data fetch by api")
        ig_accounts = []
        if len(fb_pages_id) > 0:
            for i in fb_pages_id:
                ig_aco = requests.get(
                    f"https://graph.facebook.com/v12.0/{i}?fields=instagram_business_account&access_token={access_token}")
                if "instagram_business_account" in ig_aco.json():
                    userdata = requests.get(
                        f"https://graph.facebook.com/v3.2/{ig_aco.json()['instagram_business_account']['id']}?fields=username&access_token={access_token}")
                    username = userdata.json(
                    )["username"] if "username" in userdata.json() else ""
                    ig_accounts.append(
                        {"ig_id": ig_aco.json()["instagram_business_account"]["id"], "username": username})

        for i in ig_accounts:
            check = BrandSocialAccounts.query.filter(
                BrandSocialAccounts.social_account_id == i["ig_id"], BrandSocialAccounts.brand_id == brand_id).first()
            if check:
                if check.active == False:
                    check.active = True
                    check.access_key = access_token
                    check.username = i["username"]
                    db.session.commit()
            else:
                create_db = BrandSocialAccounts(id=uuid.uuid4(), brand_id=brand_id, name="Instagram",
                                                site_link="https://instagram.com", username=i['username'], social_account_id=i['ig_id'], access_key=access_token, active=True)
                db.session.add(create_db)
                add_user_access = SocialAccess(user_id=get_active_user(
                ), brand_id=brand_id, social_id=create_db.id, active=True)
                db.session.add(add_user_access)
                log = BrandLog(id=uuid.uuid4(), user_id=get_active_user(), brand_id=brand_id,
                               message=f"Instagram - {i['username']} is added ", created_at=get_time(), date=date.today())
                db.session.add(log)
                db.session.commit()
        return {"items": ig_accounts}, HTTPStatus.CREATED
    except Exception as e:
        config.logging.critical(f"Failed to add social Instagram account:{e}")
        raise BadRequest(
            "Error in adding Social Instagram Account.")


def refresh_token(auth_code, client_id, client_secret, redirect_uri):
    try:
        access_token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        }
        response = requests.post(access_token_url, data=data, timeout=30)
        response = response.json()
        print(response)
        access_token = response['access_token']
        return access_token
    except Exception as e:
        config.logging.critical(
            f"Failed to generate linkedin access token:{e}")
        raise BadRequest(
            "Failed to generate linkedin access token.")


def li_headers(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'cache-control': 'no-cache',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    return headers


def li_user_info(headers):
    try:
        response = requests.get(
            'https://api.linkedin.com/v2/me', headers=headers)
        user_info = response.json()
        return user_info
    except Exception as e:
        config.logging.critical(f"Failed to get linkedin user info:{e}")
        raise BadRequest(
            "Failed to get linkedin user info.")


def create_social_account_linkedin(brand_id, data):
    try:
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(f"api: get brand id not valid. {e}")
        raise BadRequest("get brand id not valid.")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        config.logging.warning(
            f"api: brand social account services: Brand not available!")
        raise BadRequest("Brand not available!")
    user_id = get_active_user()
    if str(brand.user_id) != str(user_id):
        raise BadRequest("You are not authorized to add social accounts")
    if "access_token" not in data:
        raise BadRequest("please add access_token in data")
    try:
        client_id = cur_app.config["LI_CLIENT_ID"]
        client_secret = cur_app.config["LI_CLIENT_SECRET"]
        redirect_uri = cur_app.config["LI_REDIRECT_URI"]
        auth_code = data["access_token"]
        access_token = refresh_token(
            auth_code, client_id, client_secret, redirect_uri)
        if not access_token:
            raise BadRequest("Access token not able to genrate in Linkedin")
        headers = li_headers(access_token)
        user_info = li_user_info(headers)
        urn = user_info['id']
        social_account_id = f'urn:li:person:{urn}'
        first_name = user_info['localizedFirstName'] if "localizedFirstName" in user_info else ''
        last_name = user_info['localizedLastName'] if "localizedLastName" in user_info else ''
        username = first_name + ' ' + last_name
        check = BrandSocialAccounts.query.filter(
            BrandSocialAccounts.social_account_id == social_account_id, BrandSocialAccounts.brand_id == brand_id).first()
        if check:
            if check.active == False:
                check.active = True
                check.access_key = access_token
                check.username = username
                db.session.commit()
        else:
            create_db = BrandSocialAccounts(id=uuid.uuid4(), brand_id=brand_id, name="Linkedin",
                                            site_link="https://linkedin.com", username=username, social_account_id=social_account_id, access_key=access_token, active=True)
            db.session.add(create_db)
            add_user_access = SocialAccess(user_id=get_active_user(
            ), brand_id=brand_id, social_id=create_db.id, active=True)
            log = BrandLog(id=uuid.uuid4(), user_id=get_active_user(), brand_id=brand_id,
                           message=f"Linkedin - {username} is added ", created_at=get_time(), date=date.today())
            db.session.add(log)
            db.session.add(add_user_access)
            db.session.commit()
        return {"id": social_account_id, "username": username}, HTTPStatus.CREATED
    except Exception as e:
        config.logging.critical(f"Failed to add social Linkedin account:{e}")
        raise BadRequest(
            "Error in adding Social Linkedin Account.")


def remove_user_from_social_access(brand_id, social_id, data):
    try:
        uuid.UUID(social_id)
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(f"api: get social id not valid. {e}")
        raise BadRequest("get social id not valid.")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        config.logging.warning(
            f"api: brand social account services: Brand not available!")
        raise BadRequest("Brand not available!")
    social = BrandSocialAccounts.query.filter_by(id=social_id).first()
    if not social:
        config.logging.warning(
            f"api: brand social account services: Social not available!")
        raise BadRequest("Social not available!")
    active_user_id = get_active_user()
    if str(brand.user_id) != str(active_user_id):
        raise BadRequest("You are not authorized to add social accounts")
    try:
        user_id = data["user_id"]
        if str(user_id) == str(active_user_id):
            raise BadRequest("You cannot remove brand owner to get access")
        user = User.query.filter_by(id=user_id).first()
        if not user:
            config.logging.warning(
                f"api: brand social account services: data of given user not available!")
            raise BadRequest("data of given user not available!")
        available = SocialAccess.query.filter(
            SocialAccess.social_id == social_id, SocialAccess.user_id == user_id).first()
        if not available:
            raise BadRequest(
                "This user is not connected with this social account!")
        db.session.delete(available)
        log = BrandLog(id=uuid.uuid4(), user_id=brand.user_id, brand_id=brand_id,
                       message=f"Social Access - {user.email} is removed from {social.name} ", created_at=get_time(), date=date.today())
        db.session.add(log)
        db.session.commit()
        return {"message": f"{user.email} is removed from access"}
    except Exception as e:
        config.logging.critical(f"Failed to remove social access of user:{e}")
        raise BadRequest(
            f"Error in removing Social access for given user.{e}")


def add_user_to_social_access(brand_id, social_id, data):
    try:
        uuid.UUID(social_id)
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(f"api: get social id not valid. {e}")
        raise BadRequest("get social id not valid.")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        config.logging.warning(
            f"api: brand social account services: Brand not available!")
        raise BadRequest("Brand not available!")
    social = BrandSocialAccounts.query.filter_by(id=social_id).first()
    if not social:
        config.logging.warning(
            f"api: brand social account services: Social not available!")
        raise BadRequest("Social not available!")
    user_id = get_active_user()
    if str(brand.user_id) != str(user_id):
        raise BadRequest("You are not authorized to add social accounts")
    try:
        user_id = data["user_id"]
        user = User.query.filter_by(id=user_id).first()
        if not user:
            config.logging.warning(
                f"api: brand social account services: data of given user not available!")
            raise BadRequest("data of given user not available!")
        check = Membership.query.filter(
            Membership.brand_id == brand_id, Membership.user_id == user_id).first()
        if not check:
            raise BadRequest("This user is not connected with given brand")
        available = SocialAccess.query.filter(
            SocialAccess.social_id == social_id, SocialAccess.user_id == user_id).first()
        if available:
            raise BadRequest(
                "This user is already connected with this social account!")
        add = SocialAccess(user_id=user_id, social_id=social_id,
                           brand_id=brand_id, active=True)
        log = BrandLog(id=uuid.uuid4(), user_id=brand.user_id, brand_id=brand_id,
                       message=f"Social Access - {user.email} is added to {social.name} ", created_at=get_time(), date=date.today())
        db.session.add(log)
        db.session.add(add)
        db.session.commit()
        return {"message": f"{user.email} is added to give access"}
    except Exception as e:
        config.logging.critical(f"Failed to add social access of user:{e}")
        raise BadRequest(
            f"Error in adding Social access for given user.{e}")


def update_social_account(social_id, data):
    try:
        uuid.UUID(social_id)
    except Exception as e:
        config.logging.warning(f"api: get social id not valid. {e}")
        raise BadRequest("get social id not valid.")
    social = BrandSocialAccounts.query.filter_by(id=social_id).first()
    if not social:
        raise BadRequest("Social account not found !")
    try:
        for key, value in data.items():
            if getattr(social, key) != value:
                setattr(social, key, value)
        setattr(social, "updated_at", get_time())
        log = BrandLog(id=uuid.uuid4(), user_id=get_active_user(), brand_id=social.brand_id,
                       message=f"Social  - {social.name} is updates ", created_at=get_time(), date=date.today())
        db.session.add(log)
    except Exception as e:
        config.logging.critical(f"Failed to update social account:{e}")
        raise BadRequest("Update Failed in social account")
    db.session.commit()
    return social, HTTPStatus.OK


def get_social_account(social_id):
    try:
        uuid.UUID(social_id)
    except Exception as e:
        config.logging.warning(f"api: get social id not valid. {e}")
        raise BadRequest("get social id not valid.")
    social = BrandSocialAccounts.query.filter_by(id=social_id).first()
    if not social:
        raise BadRequest("Social account not found with this id!")
    return social, HTTPStatus.OK


def remove_social_account(social_id):
    try:
        uuid.UUID(social_id)
    except Exception as e:
        config.logging.warning(f"api: get social id not valid. {e}")
        raise BadRequest("get social id not valid.")
    social = BrandSocialAccounts.query.filter_by(id=social_id).first()
    if not social:
        raise BadRequest("Social account not found with given id")
    log = BrandLog(id=uuid.uuid4(), user_id=get_active_user(), brand_id=social.brand_id,
                   message=f"Social  - {social.name} is removed ", created_at=get_time(), date=date.today())
    social.active = False
    db.session.add(log)
    db.session.commit()
    return {"message": "Social account has been successfully incative for database"}, HTTPStatus.OK


def get_all_users_to_add(brand_id, social_id):
    try:
        uuid.UUID(social_id)
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(f"api: get social id not valid. {e}")
        raise BadRequest("get social id not valid.")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        config.logging.warning(
            f"api: brand social account services: Brand not available!")
        raise BadRequest("Brand not available!")
    social = BrandSocialAccounts.query.filter_by(id=social_id).first()
    if not social:
        config.logging.warning(
            f"api: brand social account services: Social not available!")
        raise BadRequest("Social not available!")

    try:
        all_user = []
        all_users = Membership.query.filter(
            Membership.brand_id == brand_id).all()
        for i in all_users:
            all_user.append(i.user_id)
        added_users = []
        check_added = SocialAccess.query.filter(
            SocialAccess.social_id == social_id).all()
        for i in check_added:
            added_users.append(i.user_id)
        for i in added_users:
            if i in all_user:
                all_user.remove(i)
        data = []
        for i in all_user:
            user = User.query.filter_by(id=i).first()
            if user:
                data.append(user)
        return {"items": data}, HTTPStatus.OK
    except Exception as e:
        config.logging.critical(f"Failed to get users data:{e}")
        raise BadRequest("Failed to get users data")


def get_all_added_users(brand_id, social_id):
    try:
        uuid.UUID(social_id)
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(f"api: get social id not valid. {e}")
        raise BadRequest("get social id not valid.")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        config.logging.warning(
            f"api: brand social account services: Brand not available!")
        raise BadRequest("Brand not available!")
    social = BrandSocialAccounts.query.filter_by(id=social_id).first()
    if not social:
        config.logging.warning(
            f"api: brand social account services: Social not available!")
        raise BadRequest("Social not available!")

    try:
        added_users = []
        check_added = SocialAccess.query.filter(
            SocialAccess.social_id == social_id).all()
        for i in check_added:
            added_users.append(i.user_id)
        data = []
        for i in added_users:
            user = User.query.filter_by(id=i).first()
            if user:
                data.append(user)
        return {"items": data}, HTTPStatus.OK
    except Exception as e:
        config.logging.critical(f"Failed to get users data:{e}")
        raise BadRequest("Failed to get users data")
