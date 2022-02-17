import calendar
import random
import time
from http import HTTPStatus

from sqlalchemy import func

from app.main import config
from app.main import db
from app.main.models.meta_static_pages import GeneratedPages


def get_layout_names(country):
    currentDate = calendar.timegm(time.gmtime())

    chosen_layout = []
    try:
        layoutGroups = GeneratedPages.query.with_entities(
            GeneratedPages.layout_name).group_by(GeneratedPages.layout_name).all()
    except Exception as e:
        config.logging.warning(f"error in generating groups.{e}")

    for content in layoutGroups:
        USCheck = False
        user_country = country
        try:
            while True:
                page = GeneratedPages.query.filter(
                    GeneratedPages.layout_name == content[0], GeneratedPages.country == user_country,
                    GeneratedPages.published_at==None, currentDate <= GeneratedPages.expires_at).order_by(func.random()).first()

                if page is not None:
                    page.published_at = currentDate
                    db.session.commit()
                    break
                user_country = "US"
                if USCheck:
                    page = GeneratedPages.query.filter(
                        GeneratedPages.layout_name == content[0], GeneratedPages.country == 'US').order_by(func.random()).first()
                    break
                USCheck = True
            chosen_layout.append(page.page_name)
        except Exception as e:
            config.logging.warning(f"error in getting layout names:{e}")
    random.shuffle(chosen_layout)
    return {"result": chosen_layout}, HTTPStatus.OK.value
