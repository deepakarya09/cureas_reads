import calendar
import time

from flask import request
from werkzeug.exceptions import Forbidden

from app.main.models.user_session import UserSession


def get_time(): return calendar.timegm(time.gmtime())


def get_user():
    headers = request.headers
    bearer = headers.get('Authorization')
    if not bearer:
        raise Forbidden("Token not Found")
    token = bearer.split()[1]
    sess = UserSession.query.filter_by(token=token).first()
    ids = sess.session.brand[0].id
    return ids

def get_active_user():
    headers = request.headers
    bearer = headers.get('Authorization')
    if not bearer:
        raise Forbidden("Token not Found")
    token = bearer.split()[1]
    sess = UserSession.query.filter_by(token=token).first()
    ids = sess.session
    return ids.id