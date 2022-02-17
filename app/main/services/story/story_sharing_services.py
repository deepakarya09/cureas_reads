import io
from PIL import Image
from app.main import config, db
from sqlalchemy import or_
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
from app.main.models.story_app import BrandStory
from app.main.models.story_share import SharingLog
from app.main.models.story_template import StoryTemplate
from app.main.services import get_active_user, get_time
import requests
from app.main.models.user import User
from app.main.services.brand_social_accounts_services import li_headers
from app.main.services.image_upload_services import upload_images_api_social
from app.main.tokenvalidation.token_check import scope
import urllib.parse
from datetime import date


def get_available_platform(brand_id, template_id):
    try:
        uuid.UUID(brand_id)
        uuid.UUID(template_id)
    except Exception as e:
        config.logging.warning(f"api: get brand id or template not valid. {e}")
        raise BadRequest("get brand id or template id not valid.")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        config.logging.warning(
            f"api: Story Sharing account services: Brand not available!")
        raise BadRequest("Brand not available!")
    template = StoryTemplate.query.filter_by(id=template_id).first()
    if not template:
        config.logging.warning(
            f"api: Story sharing services: Template not available!")
        raise BadRequest("Template not available!")
    user_id = get_active_user()
    socials = []
    get_all_accounts = BrandSocialAccounts.query.join(SocialAccess).filter(
        SocialAccess.brand_id == brand_id, SocialAccess.user_id == user_id).all()
    for i in get_all_accounts:
        if str(i.name) in template.social_support:
            if str(i.name) not in socials:
                socials.append(i.name)
    return {"socials": socials}, HTTPStatus.OK.value


def list_of_social_accounts(brand_id, name):
    try:
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(f"api: get brand id not valid. {e}")
        raise BadRequest("get brand id id not valid.")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        config.logging.warning(
            f"api: Story Sharing account services: Brand not available!")
        raise BadRequest("Brand not available!")
    user_id = get_active_user()
    get_all_accounts = BrandSocialAccounts.query.join(SocialAccess).filter(
        SocialAccess.brand_id == brand_id, SocialAccess.user_id == user_id)
    if name:
        if not (name == "Instagram" or name == "Facebook" or name == "Twitter" or name == "Linkedin"):
            config.logging.warning(
                f"api: brand social account services: please enter valid name!")
            raise BadRequest("Please enter valid name!")
    get_all_accounts = get_all_accounts.filter(
        BrandSocialAccounts.active == True)
    if name:
        get_all_accounts = get_all_accounts.filter(
            BrandSocialAccounts.name == name)
    items = get_all_accounts.order_by(BrandSocialAccounts.updated_at.desc())
    return {"items": items}, HTTPStatus.OK.value


def sharing_story(brand_id, story_id, data):
    try:
        uuid.UUID(story_id)
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(f"api: get brand id not valid. {e}")
        raise BadRequest("get brand id id not valid.")
    story = BrandStory.query.filter_by(id=story_id).first()
    if not story:
        config.logging.warning(
            f"api: Story Sharing account services: Story not available!")
        raise BadRequest("Story not available!")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        config.logging.warning(
            f"api: Story Sharing account services: Brand not available!")
        raise BadRequest("Brand not available!")
    user_id = get_active_user()
    if "schedule_time" not in data:
        raise BadRequest("Schedule time not available in given data!")
    time = data["schedule_time"]
    if data["schedule_time"] <= get_time():
        time = get_time() + 2
    if "image" not in data:
        raise BadRequest("please add image in data!")
    image = upload_images_api_social(brand_id, data)
    image_link = image["image_link"]
    try:
        for i in data["social_accounts"]:
            try:
                uuid.UUID(i)
            except Exception as e:
                config.logging.warning(
                    f"api: get social account id not valid. {e}")
                raise BadRequest("get social accounts id not valid.")
            social = BrandSocialAccounts.query.filter_by(id=i).first()
            if not social:
                config.logging.warning(
                    f"api: Story Sharing account services: Social account not available!")
                raise BadRequest("Social account not available!")

            add_to_db = SharingLog(id=uuid.uuid4(), story_id=story_id, social_id=i,
                                   user_id=user_id, brand_id=brand_id, schedule_time=time, success=False, schedule=data["schedule"], image_link=image_link, caption=data["caption"], type=data["type"], deleted=False)
            db.session.add(add_to_db)
            log = BrandLog(id=uuid.uuid4(), user_id=get_active_user(), brand_id=brand_id,
                           message=f"scheduled to share {story.story_name} on {social.name}", created_at=get_time(), date=date.today())
            db.session.add(log)
            db.session.commit()
            return add_to_db, HTTPStatus.CREATED
    except Exception as e:
        config.logging.warning(
            f"api: error in adding data for sharing log. {e}")
        raise BadRequest(f"error in adding data for sharing log.{e}")


def posting_story(log_id):
    try:
        uuid.UUID(log_id)
    except Exception as e:
        config.logging.warning(
            f"api: posting story log id not valid. {e}")
        raise BadRequest("posting story log id not valid.")
    sharing = SharingLog.query.filter_by(id=log_id).first()
    if not sharing:
        config.logging.warning(
            f"api: Story Sharing account services: sharing log not available!")
        raise BadRequest("sharing log not available!")
    social = BrandSocialAccounts.query.filter_by(id=sharing.social_id).first()
    if not social:
        config.logging.warning(
            f"api: Story Sharing account services: social account not available!")
        raise BadRequest("social acount not available!")
    story = BrandStory.query.filter_by(id=sharing.story_id).first()
    if not story:
        config.logging.warning(
            f"api: Story Sharing account services: story not available!")
        raise BadRequest("story not available!")
    try:
        if social.name == "Instagram":
            ig_user_id = social.social_account_id
            user_access_token = social.access_key
            public_http_path_to_image = sharing.image_link
            url_encoded_caption = urllib.parse.quote_plus(sharing.caption)
            creation = requests.post(
                f"https://graph.facebook.com/v10.0/{ig_user_id}/media?image_url={public_http_path_to_image}&caption={url_encoded_caption}&access_token={user_access_token}")
            if creation.status_code == 200:
                creation_id = creation.json()["id"]
                if not creation_id:
                    raise BadRequest("creation id not available")
                post = requests.post(
                    f"https://graph.facebook.com/v10.0/{ig_user_id}/media_publish?creation_id={creation_id}&access_token={user_access_token}")
                if post.status_code == 200:
                    sharing.success = True
                    sharing.posting_id = post.json()['id']
                    sharing.sharing_status = f"Success - {post.json()['id']} successfully posted"
                    log = BrandLog(id=uuid.uuid4(), user_id=sharing.user_id, brand_id=sharing.brand_id,
                                   message=f"successfully - share {story.story_name} on {social.name}", created_at=get_time(), date=date.today())
                    db.session.add(log)
                    db.session.commit()
                    return {"message": f"Successfully posted - {post.json()['id']}"}
                else:
                    sharing.retry_count = sharing.retry_count + 1
                    sharing.sharing_status = f"Error {post.status_code}- {post.json()['error']['message']}"
                    log = BrandLog(id=uuid.uuid4(), user_id=sharing.user_id, brand_id=sharing.brand_id,
                                   message=f"Error - sharing {story.story_name} on {social.name}", created_at=get_time(), date=date.today())
                    db.session.add(log)
                    db.session.commit()
                    return {"message": f"Error {post.status_code}- {post.json()['error']['message']}"}
            else:
                sharing.retry_count = sharing.retry_count + 1
                sharing.sharing_status = f"Error {creation.status_code} - {creation.json()['error']['message']}"
                social.active = False
                log = BrandLog(id=uuid.uuid4(), user_id=sharing.user_id, brand_id=sharing.brand_id,
                               message=f"Error - sharing {story.story_name} on {social.name}", created_at=get_time(), date=date.today())
                db.session.add(log)
                db.session.commit()
                return {"message": f"Error {creation.status_code}- {creation.json()['error']['message']}"}
        if social.name == "Linkedin":
            access_token = social.access_key
            li_user_id = social.social_account_id
            headers = li_headers(access_token)
            image_data = {"registerUploadRequest": {"recipes": ["urn:li:digitalmediaRecipe:feedshare-image"], "owner": f"{li_user_id}", "serviceRelationships": [{
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent"}]}}
            assets_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
            assets_upload = requests.post(
                assets_url, headers=headers, json=image_data)
            assets_upload_response = assets_upload.json()
            asset = assets_upload_response['value']['asset']
            image_URL = assets_upload_response['value']['uploadMechanism'][
                'com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            try:
                img = Image.open(io.BytesIO(requests.get(sharing.image_link, headers={
                    'User-Agent': 'Mozilla/5.0'}, timeout=28, stream=True).content))
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                bytes_im = buf.getvalue()
            except Exception as e:
                config.logging.warning(f"Faild to load image{e}")
                raise BadRequest(f"Faild to load image {e}")
            action = requests.put(image_URL, data=bytes_im, headers=headers)
            if action.status_code == 201:
                api_url = "https://api.linkedin.com/v2/ugcPosts"
                post_data = {"author": social.social_account_id,
                             "lifecycleState": "PUBLISHED",
                             "specificContent": {
                                 "com.linkedin.ugc.ShareContent": {
                                     "shareCommentary": {
                                         "text": sharing.caption,
                                     },
                                     "shareMediaCategory": "IMAGE",
                                     "media": [
                                         {
                                             "status": "READY",
                                             "description": {
                                                 "text": sharing.caption
                                             },
                                             "media": asset,
                                             "title": {
                                                 "text": story.story_name
                                             }
                                         }
                                     ]
                                 }
                             },
                             "visibility": {
                                 "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                             }
                             }
                r = requests.post(api_url, headers=headers, json=post_data)
                if r.status_code == 201:
                    sharing.success = True
                    sharing.posting_id = r.json()['id']
                    sharing.sharing_status = f"Success - {r.json()['id']} successfully posted"
                    log = BrandLog(id=uuid.uuid4(), user_id=sharing.user_id, brand_id=sharing.brand_id,
                                   message=f"successfully - share {story.story_name} on {social.name}", created_at=get_time(), date=date.today())
                    db.session.add(log)
                    db.session.commit()
                    return {"message": f"Successfully posted - {r.json()['id']}"}
                else:
                    sharing.retry_count = sharing.retry_count + 1
                    sharing.sharing_status = f"Error {r.status_code}- {r.json()['message']}"
                    log = BrandLog(id=uuid.uuid4(), user_id=sharing.user_id, brand_id=sharing.brand_id,
                                   message=f"Error - sharing {story.story_name} on {social.name}", created_at=get_time(), date=date.today())
                    db.session.add(log)
                    db.session.commit()
                    return {"message": f"Error {r.status_code}- {r.json()['message']}"}
            else:
                sharing.retry_count = sharing.retry_count + 1
                sharing.sharing_status = f"Error {action.status_code} - {action.json()['message']}"
                social.active = False
                log = BrandLog(id=uuid.uuid4(), user_id=sharing.user_id, brand_id=sharing.brand_id,
                               message=f"Error - sharing {story.story_namename} on {social.name}", created_at=get_time(), date=date.today())
                db.session.add(log)
                db.session.commit()
                return {"message": f"Error {action.status_code}- {action.json()['message']}"}
    except Exception as e:
        config.logging.warning(
            f"api: error in posting story. {e}")
        raise BadRequest(f"error in posting story.{e}")


def schedule_share(app):
    with app.app_context():
        sharings = SharingLog.query.filter(
            SharingLog.success == False, SharingLog.deleted == False, SharingLog.schedule_time <= get_time(), SharingLog.retry_count < 3).all()
        for i in sharings:
            result = posting_story(str(i.id))
            config.logging.warning(f"Sharing Log: {result['message']}")
            print(result['message'])
        print("nothing to share")


def all_sharing_logs(success, story_id, social_id, user_id, page, limit):

    try:
        if user_id:
            uuid.UUID(user_id)
            user = User.query.filter(User.id == user_id).first()
            if not user:
                config.logging.warning(
                    f"api: brand page services: Brand not available!")
                raise BadRequest("Brand not available!")
        if story_id:
            uuid.UUID(story_id)
            story = Brand.query.filter(id=story_id).first()
            if not story:
                config.logging.warning(
                    f"api: brand page services: Brand not available!")
                raise BadRequest("Brand not available!")
        if social_id:
            uuid.UUID(social_id)
            social = BrandSocialAccounts.query.filter(
                BrandSocialAccounts.id == social_id).first()
            if not social:
                config.logging.warning(
                    f"api: get all sharing log: Social not available!")
                raise BadRequest("Social Account not available!")
    except Exception as e:
        config.logging.warning(
            f"api: error in geting id. {e}")
        raise BadRequest(f"error in getting id wrong id.{e}")

    mm = SharingLog.query.filter(SharingLog.deleted == False)
    if success:
        mm = mm.filter(SharingLog.success == success)
    if story_id:
        mm = mm.filter(SharingLog.story_id == story_id)
    if social_id:
        mm = mm.filter(SharingLog.social_id == social_id)
    if user_id:
        mm = mm.filter(SharingLog.user_id == user_id)
    item = mm.order_by(SharingLog.created_at.desc())

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
                }, HTTPStatus.OK
    except Exception as e:
        config.logging.error(
            f"api: get all sharing logs : not able to return ecouse at some point of database . {e}")
        raise BadRequest(
            f"Not able to return becouse at some point of database. {e}")


def sharing_log_marketing(brand_id, page, limit, search):
    try:
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(
            f"api: Get story log brand id not valid. {e}")
        raise BadRequest("Get story log brand id not valid.")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        config.logging.warning(
            f"api: Story Sharing account services: Brand not available!")
        raise BadRequest("Brand not available!")
    if search:
        searchkey = "%{}%".format(search)
        log = SharingLog.query.order_by(SharingLog.created_at.desc()).filter(
            SharingLog.brand_id == brand_id, SharingLog.deleted == False).filter(or_(SharingLog.caption.ilike(searchkey))).paginate(
            page=page, per_page=limit)
    else:
        log = SharingLog.query.order_by(SharingLog.created_at.desc()).filter(
            SharingLog.brand_id == brand_id, SharingLog.deleted == False).paginate(page=page, per_page=limit)
    objects = log.items
    items = []
    for i in objects:
        data = {}
        data.update({'id': i.id, 'image_link': i.image_link, 'schedule_time': i.schedule_time, 'success': i.success,
                    'schedule': i.schedule, 'sharing_status': i.sharing_status, 'caption': i.caption, 'posting_id': i.posting_id})
        social = BrandSocialAccounts.query.filter(
            BrandSocialAccounts.id == i.social_id).first()
        soc = {}
        soc.update({'id': social.id, "name": social.name,
                   'username': social.username})
        data.update({"account": soc})
        story = BrandStory.query.filter(BrandStory.id == i.story_id).first()
        sto = {}
        sto.update({'id': story.id, 'name': story.story_name,
                   "link": story.story_link})
        data.update({"story": sto})
        items.append(data)

    total_page = [page for page in log.iter_pages()]

    if not log:
        return {"items": []}, HTTPStatus.OK.value
    try:
        return {"items": items,
                "total_pages": total_page if total_page else [],
                "pages": log.pages,
                "has_next": log.has_next,
                "has_prev": log.has_prev,
                "page": log.page,
                "per_page": log.per_page,
                "total": log.total,
                }, HTTPStatus.OK
    except Exception as e:
        config.logging.error(
            f"api: get all sharing logs : not able to return ecouse at some point of database . {e}")
        raise BadRequest(
            f"Not able to return becouse at some point of database. {e}")
