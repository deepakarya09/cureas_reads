from http import HTTPStatus
from sqlalchemy import func
from app.main.models.contents import Content
from app.main import db


def get_all_contents(used):
    content = Content.query.with_entities(Content.country).filter_by(used=used).group_by(Content.country).all()
    items = []
    for contents in content:
        con = Content.query.filter_by(country=contents[0], used=used).order_by(func.random()).all()
        for c in con:
            c.used = True
            db.session.commit()
        items.append(con)
    return {"items": items}, HTTPStatus.OK.value


