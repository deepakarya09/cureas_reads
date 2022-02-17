import calendar
import time
import uuid
from http import HTTPStatus

from sqlalchemy import func
from werkzeug.exceptions import BadRequest

from app.main import config
from app.main import db
from app.main.models.user import User
from app.main.models.token import Token
from app.main.services import get_time
import random
import string

def ran_gen(size, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def create_referral(data):
    created_by = data['created_by']
    user = User.query.filter_by(id=created_by).first()
    if not user:
        raise BadRequest("User not available in database. Please check user id.")
    try:
        create = Token(
            id = uuid.uuid4(),
            code = ran_gen(6,f'CU87RXYZA863BD7E{data["count"]}'),
            created_by = data["created_by"],
            count = data["count"],
            created_at = get_time()
        ) 
        db.session.add(create)
        db.session.commit()
        return create
    except Exception as e:
        raise BadRequest(f"Not able to create referral code due to {e}")