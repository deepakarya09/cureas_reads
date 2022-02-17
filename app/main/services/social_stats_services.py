import uuid
import requests
from http import HTTPStatus
from bs4 import BeautifulSoup
from werkzeug.exceptions import BadRequest
from app.main import config
from datetime import date
from flask import current_app as cur_app
from app.main.models.social_stats import SocialStats
from app.main import db

from app.main.models.story_share import SharingLog


def add_social_status(id):
    i = SharingLog.query.filter_by(id=id).first()
    if not i:
        raise BadRequest("Sharing Log with given id is not found")
    try:
        if i.sharing_log.name == "Instagram":
            posting_id = i.posting_id
            user_access_token = i.sharing_log.access_key
            req = requests.get(
                f"https://graph.facebook.com/v12.0/{posting_id}?fields=id,media_type,media_url,owner,timestamp,like_count,comments_count&access_token={user_access_token}")
            if req.status_code == 200:
                likes = req.json()["like_count"]
                comments = req.json()["comments_count"]
                req2 = requests.get(
                    f"https://graph.facebook.com/v12.0/{posting_id}/insights?metric=impressions,reach,engagement&access_token={user_access_token}")
                if req2.status_code == 200:
                    for j in range(len(req2.json()["data"])):
                        if req2.json()["data"][j]["name"] == "impressions":
                            impression = req2.json()[
                                "data"][j]["values"][0]["value"]
                        if req2.json()["data"][j]["name"] == "engagement":
                            engagement = req2.json()[
                                "data"][j]["values"][0]["value"]
                else:
                    pass
                today = date.today()
                check = SocialStats.query.filter(
                    SocialStats.sharing_id == i.id, SocialStats.date == today).first()
                if check:
                    check.likes = likes if likes else 0
                    check.comments = comments if comments else 0
                    check.views = impression if impression else 0
                    check.interaction = engagement if engagement else 0
                else:
                    create = SocialStats(id=uuid.uuid4(), social_id=i.social_id, brand_id=i.brand_id, sharing_id=i.id, likes=likes, comments=comments, views=impression, interaction=engagement, account_type=i.sharing_log.name
                                         )
                    db.session.add(create)
                db.session.commit()
                return {"message": f"record added"}
            else:
                dels = SocialStats.query.filter(
                    SocialStats.sharing_id == i.id).all()
                if dels:
                    db.session.delete(dels)
                i.deleted = True
                i.success = False
                db.session.commit()
                return {"message": f"error in adding"}
        if i.sharing_log.name == "Linkedin":
            pass
    except Exception as e:
        config.logging.critical(
            f"Not able to likes and comments for social id {e}")
        raise BadRequest("Not able to likes and comments for social id.")


def call_scheduler_for_social_logs(app):
    with app.app_context():
        all_logs = SharingLog.query.filter(
            SharingLog.success == True, SharingLog.deleted == False).all()
        for i in all_logs:
            result = add_social_status(str(i.id))
            config.logging.warning(f"social Stats: {result['message']}")
            print(result['message'])
        print("nothing to add for likes and comments")
