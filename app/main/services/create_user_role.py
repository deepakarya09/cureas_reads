from app.main.models.rolebranduser import RoleBrandUser
import uuid
from http import HTTPStatus
from werkzeug.exceptions import BadRequest
from app.main import db


def create_role(data):
    role = RoleBrandUser.query.filter_by(name=data["name"]).first()
    if role:
        raise BadRequest(f"This {role.name} already exists")
    try:
        create = RoleBrandUser(
            id = uuid.uuid4(),
            name = data["name"]
        ) 
        db.session.add(create)
        db.session.commit()
        return create
    except Exception as e:
        raise BadRequest(f"Error in creating role due to :  {e}")

def all_role():
    return {"items": RoleBrandUser.query.all()}, HTTPStatus.OK.value