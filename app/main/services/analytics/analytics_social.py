from http import HTTPStatus
import uuid
from app.main import config, db
from werkzeug.exceptions import BadRequest
from datetime import date, timedelta
from app.main.models.brand_social_accounts import BrandSocialAccounts
from app.main.models.brands import Brand
from app.main.models.social_stats import SocialStats
from app.main.models.story_share import SharingLog
import sqlalchemy as sq


def social_analytics(brand_id, interval):
    if not interval:
        raise BadRequest(
            f"Please add interval to get filter data Day, Week or Month.")
    if not (interval == "Day" or interval == "Week" or interval == "Month"):
        raise BadRequest(
            f"Please add interval to get filter data Day, Week or Month.")
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
    gap = 0
    if interval:
        if interval == "Day":
            gap = 1
        if interval == "Week":
            gap = 7
        if interval == "Month":
            gap = 30
    days = date.today()
    past_days = date.today() - timedelta(days=gap)
    gap_days = past_days - timedelta(days=gap)
    data = SharingLog.query.filter(SharingLog.brand_id == brand_id,
                                   SharingLog.date >= past_days, SharingLog.success == True, SharingLog.deleted == False).all()
    past_data = SharingLog.query.filter(SharingLog.brand_id == brand_id,
                                        SharingLog.date >= gap_days, SharingLog.date <= past_days, SharingLog.success == True, SharingLog.deleted == False).all()
    total_post = int(len(data))
    past_total_post = len(past_data)
    post_percentage = 0 if past_total_post == 0 and total_post == 0 else (
        ((total_post/past_total_post)*100)-100) if past_total_post != 0 and total_post == 0 else 100

    subquery1 = db.session.query(SharingLog.id).filter(
        SharingLog.brand_id == brand_id,
        SharingLog.date >= past_days, SharingLog.success == True, SharingLog.deleted == False).subquery()
    stats1 = db.session.query(SocialStats).with_entities(sq.func.sum(SocialStats.likes).label('likes'), sq.func.sum(SocialStats.comments).label('comment')).filter(
        SocialStats.sharing_id.in_(subquery1), SocialStats.brand_id == brand_id, SocialStats.date == days).first()

    subquery2 = db.session.query(SharingLog.id).filter(
        SharingLog.brand_id == brand_id,
        SharingLog.date <= past_days, SharingLog.date >= past_days, SharingLog.success == True, SharingLog.deleted == False).subquery()
    stats2 = db.session.query(SocialStats).with_entities(sq.func.sum(SocialStats.likes).label('likes'), sq.func.sum(SocialStats.comments).label('comment')).filter(
        SocialStats.sharing_id.in_(subquery2), SocialStats.brand_id == brand_id, SocialStats.date == past_days).first()
    likes = int(stats1.likes) if stats1.likes else 0
    past_likes = int(stats2.likes) if stats2.likes else 0
    comments = int(stats1.comment) if stats1.comment else 0
    past_comments = int(stats2.comment) if stats2.comment else 0
    likes_percentage = 0 if past_likes == 0 and likes == 0 else (
        ((likes/past_likes)*100)-100) if past_likes != 0 and likes == 0 else 100
    comment_percentage = 0 if past_comments == 0 and comments == 0 else (
        ((comments/past_comments)*100)-100) if past_comments != 0 and comments == 0 else 100
    lis = []
    accounts = BrandSocialAccounts.query.filter(
        BrandSocialAccounts.brand_id == brand_id, BrandSocialAccounts.active == True).all()
    for i in accounts:
        account_post = SharingLog.query.filter(
            SharingLog.social_id == i.id, SharingLog.success == True, SharingLog.deleted == False, SharingLog.date >= past_days).all()
        past_account_post = SharingLog.query.filter(
            SharingLog.social_id == i.id, SharingLog.success == True, SharingLog.deleted == False, SharingLog.date >= gap_days).all()
        account_likes = 0
        account_comments = 0
        account_past_likes = 0
        account_past_comments = 0
        for k in account_post:
            t = SocialStats.query.filter(
                SocialStats.date == days, SocialStats.brand_id == brand_id, SocialStats.sharing_id == k.id).first()
            if t:
                account_likes = t.likes + account_likes
                account_comments = t.comments + account_comments
        for j in past_account_post:
            p = SocialStats.query.filter(
                SocialStats.date == past_days, SocialStats.brand_id == brand_id, SocialStats.sharing_id == j.id).first()
            if p:
                account_past_likes = p.likes + account_past_likes
                account_past_comments = p.comments + account_past_comments
        account_likes_percentage = 0 if account_past_likes == 0 and account_likes == 0 else (
            ((account_likes/account_past_likes)*100)-100) if account_past_likes != 0 and account_likes == 0 else 100
        account_comment_percentage = 0 if account_past_comments == 0 and account_comments == 0 else (
            ((account_comments/account_past_comments)*100)-100) if account_past_comments != 0 and account_comments == 0 else 100
        d = {
            "name": i.name,
            "username": i.username,
            "total_post": int(len(account_post)),
            "total_likes": account_likes,
            "likes_percent": account_likes_percentage,
            "total_comments": account_comments,
            "comment_percent": account_comment_percentage
        }
        lis.append(d)
    return {"items": lis, "total_post": total_post, "post_percentage": post_percentage, "total_likes": likes, "likes_percentage": likes_percentage, "total_comments": comments, "comments_percentage": comment_percentage}, HTTPStatus.OK


def get_anylitics_by_sharing_id(sharing_id):
    try:
        uuid.UUID(sharing_id)
    except Exception as e:
        config.logging.warning(
            f"Api: Get analysis : Invalid submission - Sharing Id: {sharing_id}.")
        raise BadRequest(f"This {sharing_id} - Sharing id is not valid.")
    data = SharingLog.query.filter(
        SharingLog.id == sharing_id, SharingLog.success == True, SharingLog.deleted == False).first()
    if not data:
        raise BadRequest(
            "Sharing Log not available in database. Please check sharing id.")
    analytics = SocialStats.query.filter(SocialStats.sharing_id == data.id).order_by(
        SocialStats.created_at.desc()).first()
    return {"image": data.image_link, "views": analytics.views if analytics else None, "interaction": analytics.interaction if analytics else None, "comments": analytics.comments if analytics else None, "likes": analytics.likes if analytics else None}
