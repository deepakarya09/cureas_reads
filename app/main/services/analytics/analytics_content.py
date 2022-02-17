from http import HTTPStatus
from sys import api_version
import time
import uuid

from pyrsistent import v
from app.main import config, db
from werkzeug.exceptions import BadRequest
from datetime import date, timedelta, datetime
from app.main.models.branding_pages import BrandPages
from app.main.models.brands import Brand
import json
from itsdangerous import URLSafeTimedSerializer
from kafka import KafkaProducer, KafkaConsumer
import requests
from app.main.models.page_stats import PageStats
from app.main.models.story_app import BrandStory
from app.main.models.story_stats import StoryStats
import sqlalchemy as sq
from app.main.services import get_time
from json import loads

auth_s = URLSafeTimedSerializer(config.Config.SECRET_KEY, "auth")

TOPIC_NAME = config.Config.KAFKA_TOPIC


def json_serializer(data):
    return json.dumps(data).encode("utf-8")


producer = KafkaProducer(
    bootstrap_servers=['34.135.67.176:9092'], api_version=(0, 9), value_serializer=lambda v: json.dumps(v).encode('utf-8'))

consumer = KafkaConsumer(
    TOPIC_NAME,
    api_version=(0, 9),
    bootstrap_servers=['34.135.67.176:9092'],
    auto_offset_reset='earliest',
    auto_commit_interval_ms=500,
    group_id="group_1",
    enable_auto_commit=True,
    value_deserializer=lambda x: loads(x.decode('utf-8')))


def producer_kafka(data, ip, device):
    try:
        content_id = auth_s.dumps(data["content_id"])
        type = "page" if "page" in data["link"] else "story"
        dat = date.today()
        da = dat.strftime("%Y-%m-%d")
        d = {
            "type": type,
            "content_id": content_id,
            "ip": ip,
            "device": device,
            "date": da,
            "created_at": get_time()
        }
        producer.send(TOPIC_NAME, d)
        producer.flush()
        return {"message": "Created"}, HTTPStatus.OK
    except Exception as e:
        config.logging.warning(f"Kafka Data saving Failed {e}")
        raise BadRequest(f"Kafka Data saving Failed {e}")


def save_to_db(data):
    ip = data["ip"]
    if (data["device"]).lower() == "windows" or (data["device"]).lower() == "linux" or (data["device"]).lower() == "darwin":
        device = "Desktop"
    else:
        device = "Mobile"
    url = 'http://ip-api.com/json/{}'.format(ip)
    r = requests.get(url)
    j = json.loads(r.text)
    if j["status"] == "fail":
        city = ""
    else:
        city = j["city"]
    dat = data["date"]
    created_at = data["created_at"]
    id = auth_s.loads(data["content_id"])
    type = data["type"]
    if type == "story":
        check = BrandStory.query.filter_by(id=id).first()
        if check:
            check2 = StoryStats.query.filter(
                StoryStats.ip == ip, StoryStats.date == dat).first()
            if check2:
                check2.views = check2.views + 1
            else:
                create = StoryStats(id=uuid.uuid4(), story_id=id, brand_id=check.brand_id,
                                    views=1, ip=ip, location=city, device=device, date=dat, created_at=created_at)
                db.session.add(create)
            db.session.commit()
        else:
            config.logging.warning(f"wrong story id in one story")
    if type == "page":
        check = BrandPages.query.filter_by(id=id).first()
        if check:
            check2 = PageStats.query.filter(
                PageStats.ip == ip, PageStats.date == dat).first()
            if check2:
                check2.views = check2.views + 1
            else:
                create = PageStats(id=uuid.uuid4(), page_id=id, brand_id=check.brand_id,
                                   views=1, ip=ip, location=city, device=device, date=dat, created_at=created_at)
                db.session.add(create)
            db.session.commit()
        else:
            config.logging.warning(f"wrong page id in one page")


def kafka_consumer(app):
    with app.app_context():
        try:
            for inf in consumer:
                data = inf.value
                print(data)
                save_to_db(data)
        except Exception as e:
            config.logging.warning(f"Kafka Data saving Failed {e}")
            raise BadRequest(f"Kafka Data saving Failed {e}")
        print("end")
        return {"message": "gjh"}, HTTPStatus.OK


def total_views_content(brand_id, interval):
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

    # Time calculation ------>
    days = get_time()
    date_time = datetime.fromtimestamp(days)
    gap_min = date_time - timedelta(days=gap)
    past_days = datetime.strptime(
        str(gap_min), '%Y-%m-%d %H:%M:%S').timestamp()
    gap_min2 = gap_min - timedelta(days=gap)
    past_days2 = datetime.strptime(
        str(gap_min2), '%Y-%m-%d %H:%M:%S').timestamp()
    # Time calculation end ----->

    total_views = 0
    total_past_views = 0
    #   Current views ---->>>
    pagequery1 = db.session.query(BrandPages.id).filter(
        BrandPages.brand_id == brand_id,
        BrandPages.created_at >= past_days, BrandPages.status == "PUBLISHED", BrandPages.active == True).subquery()
    pagestats1 = db.session.query(PageStats).with_entities(sq.func.sum(PageStats.views).label('views')).filter(
        PageStats.page_id.in_(pagequery1), PageStats.brand_id == brand_id, PageStats.created_at >= past_days).first()
    total_views = total_views + \
        int(pagestats1.views) if pagestats1.views else 0
    storyquery1 = db.session.query(BrandStory.id).filter(
        BrandStory.brand_id == brand_id,
        BrandStory.created_at >= past_days, BrandStory.status == "PUBLISHED", BrandStory.active == True).subquery()
    storystats1 = db.session.query(StoryStats).with_entities(sq.func.sum(StoryStats.views).label('views')).filter(
        StoryStats.story_id.in_(storyquery1), StoryStats.brand_id == brand_id, StoryStats.created_at >= past_days).first()
    total_views = total_views + \
        int(storystats1.views) if storystats1.views else 0
    # current views end --->

    # past views --->
    pagequery2 = db.session.query(BrandPages.id).filter(
        BrandPages.brand_id == brand_id,
        BrandPages.created_at >= past_days2, BrandPages.created_at <= past_days, BrandPages.status == "PUBLISHED", BrandPages.active == True).subquery()
    pagestats2 = db.session.query(PageStats).with_entities(sq.func.sum(PageStats.views).label('views')).filter(
        PageStats.page_id.in_(pagequery2), PageStats.brand_id == brand_id, PageStats.created_at <= past_days, PageStats.created_at >= past_days2).first()
    total_past_views = total_past_views + \
        int(pagestats2.views) if pagestats2.views else 0
    storyquery2 = db.session.query(BrandStory.id).filter(
        BrandStory.brand_id == brand_id,
        BrandStory.created_at >= past_days2, BrandStory.created_at <= past_days, BrandStory.status == "PUBLISHED", BrandStory.active == True).subquery()
    storystats2 = db.session.query(StoryStats).with_entities(sq.func.sum(StoryStats.views).label('views')).filter(
        StoryStats.story_id.in_(storyquery2), StoryStats.brand_id == brand_id, StoryStats.created_at >= past_days2, StoryStats.created_at <= past_days).first()
    total_past_views = total_past_views + \
        int(storystats2.views) if storystats2.views else 0

    # past views end ---->

    percentage = 0 if total_past_views == 0 and total_views == 0 else (
        ((total_views/total_past_views)*100)-100) if total_past_views != 0 and total_views == 0 else 100

    return {"total_views": total_views, "percentage": percentage}, HTTPStatus.OK


def recent_published_content_pages(brand_id, interval, page, limit):
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

    # Time calculation ------>
    days = get_time()
    date_time = datetime.fromtimestamp(days)
    gap_min = date_time - timedelta(days=gap)
    past_days = datetime.strptime(
        str(gap_min), '%Y-%m-%d %H:%M:%S').timestamp()
    gap_min2 = gap_min - timedelta(days=gap)
    past_days2 = datetime.strptime(
        str(gap_min2), '%Y-%m-%d %H:%M:%S').timestamp()
    # Time calculation end ----->

    post = BrandPages.query.order_by(BrandPages.created_at.desc()).filter(
        BrandPages.brand_id == brand_id,
        BrandPages.created_at >= past_days, BrandPages.status == "PUBLISHED", BrandPages.active == True).paginate(page=page, per_page=limit)
    objects = post.items
    items = []
    for i in objects:
        views = PageStats.query.with_entities(sq.func.sum(PageStats.views).label('views')).filter(
            PageStats.page_id == i.id, PageStats.created_at >= past_days).first()
        past_views = PageStats.query.with_entities(sq.func.sum(PageStats.views).label('views')).filter(
            PageStats.page_id == i.id, PageStats.created_at <= past_days, PageStats.created_at >= past_days2).first()
        v = int(views.views) if views.views else 0
        past_v = int(past_views.views) if past_views.views else 0
        percentage = 0 if past_v == 0 and v == 0 else (
            ((v/past_v)*100)-100) if past_v != 0 and v == 0 else 100
        d = {
            "name": i.page_name,
            "link": i.cdn_html_page_link,
            "image": i.thumbnail_image,
            "published_at": i.created_at,
            "views": v,
            "percentage": percentage
        }
        items.append(d)
    total_page = [page for page in post.iter_pages()]

    if not post:
        return {"items": []}, HTTPStatus.OK.value
    try:
        return {"items": items,
                "total_pages": total_page if total_page else [],
                "pages": post.pages,
                "has_next": post.has_next,
                "has_prev": post.has_prev,
                "page": post.page,
                "per_page": post.per_page,
                "total": post.total,
                }, HTTPStatus.OK
    except Exception as e:
        config.logging.error(
            f"api: get recent content : not able to return ecouse at some point of database . {e}")
        raise BadRequest(
            f"Not able to return becouse at some point of database. {e}")


def recent_published_content_storys(brand_id, interval, page, limit):
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

    # Time calculation ------>
    days = get_time()
    date_time = datetime.fromtimestamp(days)
    gap_min = date_time - timedelta(days=gap)
    past_days = datetime.strptime(
        str(gap_min), '%Y-%m-%d %H:%M:%S').timestamp()
    gap_min2 = gap_min - timedelta(days=gap)
    past_days2 = datetime.strptime(
        str(gap_min2), '%Y-%m-%d %H:%M:%S').timestamp()
    # Time calculation end ----->

    post = BrandStory.query.order_by(BrandStory.created_at.desc()).filter(
        BrandStory.brand_id == brand_id,
        BrandStory.created_at >= past_days, BrandStory.status == "PUBLISHED", BrandStory.active == True).paginate(page=page, per_page=limit)
    objects = post.items
    items = []
    for i in objects:
        views = StoryStats.query.with_entities(sq.func.sum(StoryStats.views).label('views')).filter(
            StoryStats.story_id == i.id, StoryStats.created_at >= past_days).first()
        past_views = StoryStats.query.with_entities(sq.func.sum(StoryStats.views).label('views')).filter(
            StoryStats.story_id == i.id, StoryStats.created_at <= past_days, StoryStats.created_at >= past_days2).first()
        v = int(views.views) if views.views else 0
        past_v = int(past_views.views) if past_views.views else 0
        percentage = 0 if past_v == 0 and v == 0 else (
            ((v/past_v)*100)-100) if past_v != 0 and v == 0 else 100
        d = {
            "name": i.story_name,
            "link": i.story_link,
            "image": i.thumbnail_image,
            "published_at": i.created_at,
            "views": v,
            "percentage": percentage
        }
        items.append(d)
    total_page = [page for page in post.iter_pages()]

    if not post:
        return {"items": []}, HTTPStatus.OK.value
    try:
        return {"items": items,
                "total_pages": total_page if total_page else [],
                "pages": post.pages,
                "has_next": post.has_next,
                "has_prev": post.has_prev,
                "page": post.page,
                "per_page": post.per_page,
                "total": post.total,
                }, HTTPStatus.OK
    except Exception as e:
        config.logging.error(
            f"api: get recent content : not able to return ecouse at some point of database . {e}")
        raise BadRequest(
            f"Not able to return becouse at some point of database. {e}")


def graph_analytics(brand_id, interval):
    if not interval:
        raise BadRequest(
            f"Please add interval to get filter Day, Month or Year.")
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
        if interval == "Month":
            gap = 30
        if interval == "Year":
            gap = 365
    today = date.today()
    past_days1 = today - timedelta(days=gap)
    past_days2 = past_days1 - timedelta(days=gap)
    past_days3 = past_days2 - timedelta(days=gap)
    past_days4 = past_days3 - timedelta(days=gap)
    past_days5 = past_days4 - timedelta(days=gap)
    past_days6 = past_days5 - timedelta(days=gap)
    past_days7 = past_days6 - timedelta(days=gap)

    views1_desktop = PageStats.query.with_entities(sq.func.sum(PageStats.views).label('views')).filter(
        PageStats.brand_id == brand_id, PageStats.date > past_days1, PageStats.device == "Desktop").first()
    views2_desktop = PageStats.query.with_entities(sq.func.sum(PageStats.views).label('views')).filter(
        PageStats.brand_id == brand_id, PageStats.date <= past_days1, PageStats.date > past_days2, PageStats.device == "Desktop").first()
    views3_desktop = PageStats.query.with_entities(sq.func.sum(PageStats.views).label('views')).filter(
        PageStats.brand_id == brand_id, PageStats.date <= past_days2, PageStats.date > past_days3, PageStats.device == "Desktop").first()
    views4_desktop = PageStats.query.with_entities(sq.func.sum(PageStats.views).label('views')).filter(
        PageStats.brand_id == brand_id, PageStats.date <= past_days3, PageStats.date > past_days4, PageStats.device == "Desktop").first()
    views5_desktop = PageStats.query.with_entities(sq.func.sum(PageStats.views).label('views')).filter(
        PageStats.brand_id == brand_id, PageStats.date <= past_days4, PageStats.date > past_days5, PageStats.device == "Desktop").first()
    views6_desktop = PageStats.query.with_entities(sq.func.sum(PageStats.views).label('views')).filter(
        PageStats.brand_id == brand_id, PageStats.date <= past_days5, PageStats.date > past_days6, PageStats.device == "Desktop").first()
    views7_desktop = PageStats.query.with_entities(sq.func.sum(PageStats.views).label('views')).filter(
        PageStats.brand_id == brand_id, PageStats.date <= past_days6, PageStats.date > past_days7, PageStats.device == "Desktop").first()

    views1_mobile = PageStats.query.with_entities(sq.func.sum(PageStats.views).label('views')).filter(
        PageStats.brand_id == brand_id, PageStats.date > past_days1, PageStats.device == "Mobile").first()
    views2_mobile = PageStats.query.with_entities(sq.func.sum(PageStats.views).label('views')).filter(
        PageStats.brand_id == brand_id, PageStats.date <= past_days1, PageStats.date > past_days2, PageStats.device == "Mobile").first()
    views3_mobile = PageStats.query.with_entities(sq.func.sum(PageStats.views).label('views')).filter(
        PageStats.brand_id == brand_id, PageStats.date <= past_days2, PageStats.date > past_days3, PageStats.device == "Mobile").first()
    views4_mobile = PageStats.query.with_entities(sq.func.sum(PageStats.views).label('views')).filter(
        PageStats.brand_id == brand_id, PageStats.date <= past_days3, PageStats.date > past_days4, PageStats.device == "Mobile").first()
    views5_mobile = PageStats.query.with_entities(sq.func.sum(PageStats.views).label('views')).filter(
        PageStats.brand_id == brand_id, PageStats.date <= past_days4, PageStats.date > past_days5, PageStats.device == "Mobile").first()
    views6_mobile = PageStats.query.with_entities(sq.func.sum(PageStats.views).label('views')).filter(
        PageStats.brand_id == brand_id, PageStats.date <= past_days5, PageStats.date > past_days6, PageStats.device == "Mobile").first()
    views7_mobile = PageStats.query.with_entities(sq.func.sum(PageStats.views).label('views')).filter(
        PageStats.brand_id == brand_id, PageStats.date <= past_days6, PageStats.date > past_days7, PageStats.device == "Mobile").first()

    views_desktop = [int(views7_desktop.views) if views7_desktop.views else 0, int(views6_desktop.views) if views6_desktop.views else 0, int(views5_desktop.views) if views5_desktop.views else 0, int(
        views4_desktop.views) if views4_desktop.views else 0, int(views3_desktop.views) if views3_desktop.views else 0, int(views2_desktop.views) if views2_desktop.views else 0, int(views1_desktop.views)if views1_desktop.views else 0]
    views_mobile = [int(views7_mobile.views) if views7_mobile.views else 0, int(views6_mobile.views)if views6_mobile.views else 0, int(views5_mobile.views) if views5_mobile.views else 0, int(
        views4_mobile.views) if views4_mobile.views else 0, int(views3_mobile.views) if views3_mobile.views else 0, int(views2_mobile.views) if views2_mobile.views else 0, int(views1_mobile.views)if views1_mobile.views else 0]
    data = [past_days6, past_days5, past_days4,
            past_days3, past_days2, past_days1, today]

    return{"views_desktop": views_desktop, "views_mobile": views_mobile, "data": data}, HTTPStatus.OK
