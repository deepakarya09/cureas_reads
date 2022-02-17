from functools import wraps

from flask import request
from werkzeug.exceptions import Forbidden
from app.main.models.membership import Membership
from app.main.models.rolebranduser import RoleBrandUser

from app.main.models.user_session import UserSession


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        headers = request.headers
        bearer = headers.get('Authorization')  # Bearer YourTokenHere
        if not bearer:
            raise Forbidden("Token not Found")
        token = bearer.split()[1]
        user = UserSession.query.filter_by(token=token).first()
        if not user:
            raise Forbidden("Token is invalid")

        return f(*args, **kwargs)

    return decorated

def scope(scope_name):
    def wrap(f):
        @wraps(f)
        def inner_wrapper(*args, **kwargs):
            headers = request.headers
            bearer = headers.get('Authorization')  # Bearer YourTokenHere
            if not bearer:
                raise Forbidden("Token not Found")
            token = bearer.split()[1]
            sess = UserSession.query.filter_by(token=token).first()
            if not sess:
                raise Forbidden("Token is invalid")
            ids = sess.session.id
            check_permission = RoleBrandUser.query.join(Membership).filter(Membership.user_id == ids).filter(Membership.active==True).first()
            if not check_permission:
                raise Forbidden("You don't have permission to access any brand")
            if (scope_name == 'get' and check_permission.name == 'Editor') or (scope_name == 'post' and check_permission.name == 'Editor'):
                return f(*args, **kwargs)
            if (scope_name == 'get' and check_permission.name == 'Admin') or (scope_name == 'post' and check_permission.name == 'Admin') or (scope_name == 'put' and check_permission.name == 'Admin'):
                return f(*args, **kwargs)
            if (scope_name == 'get' and check_permission.name == 'Owner') or (scope_name == 'post' and check_permission.name == 'Owner') or (scope_name == 'put' and check_permission.name == 'Owner')  or (scope_name == 'delete' and check_permission.name == 'Owner'):
                return f(*args, **kwargs)
            raise Forbidden("You don't have permission to access.")
        return inner_wrapper
    return wrap