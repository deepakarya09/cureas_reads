import uuid
from app.main.models.brand_log import BrandLog
from app.main.models.membership import Membership
from app.main.models.rolebranduser import RoleBrandUser
from app.main.services import get_time
from app.main.services.user_service import sign_up
from app.main.services.user_registration_confirmation_mail import send_confirmation_email
from werkzeug.exceptions import BadRequest
from app.main import config
from app.main import db
from app.main.models.brands import Brand
from app.main.models.user import User
from itsdangerous import URLSafeTimedSerializer
from datetime import date

auth_s = URLSafeTimedSerializer(config.Config.SECRET_KEY, "auth")


def email_confirmation(data):
    email = data['email']
    brand_id = data['brand_id']

    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        raise BadRequest("Brand not found id database. Please check brand id")
    role = RoleBrandUser.query.filter_by(name="Editor").first()
    if not role:
        raise BadRequest(
            "Editor Role not found in database. Please add in database to assign")
    user = User.query.filter_by(email=email).first()

    if user:
        available = Membership.query.filter_by(
            user_id=user.id).filter_by(brand_id=brand_id).first()
        if available:
            raise BadRequest(
                f"{email} This user is already having this brand.")
        try:
            add = Membership(
                user_id=user.id,
                brand_id=brand_id,
                role_id=role.id
            )
            db.session.add(add)
            log = BrandLog(id=uuid.uuid4(), user_id=brand.user_id, brand_id=brand_id,
                           message=f"{email} added in brand", created_at=get_time(), date=date.today())
            db.session.add(log)
            db.session.commit()
            return{
                "message": f"This Brand added successfully to {email}"
            }
        except Exception as e:
            config.logging.error(f"error in assigning brand to user.{e}")
            raise BadRequest(f"error in assigning brand to user.{e}")
    else:
        try:
            message = send_confirmation_email(email, brand_id)
            return{
                "message": message
            }
        except Exception as e:
            config.logging.error(
                f"error in sending confirmation mail to {email}.{e}")
            raise BadRequest(f"error in sending confirmation mail to {email}.")


def add_new_user_and_confirm_code(data, confirmation):
    try:
        value = auth_s.loads(confirmation, max_age=172800)
    except Exception as e:
        raise BadRequest(
            f"confirmation link not valid or expired please resend")
    if "email" not in value or "brand_id" not in value:
        raise BadRequest("Confirmation Link is not valid")
    brand_id = value["brand_id"]
    email_id = value["email"]
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        raise BadRequest("Confirmation link is not valid")
    signup_data = {
        "email": email_id,
        "login_type": "system",
        "password": data["password"]
    }
    role = RoleBrandUser.query.filter_by(name="Editor").first()
    if not role:
        raise BadRequest(
            "Editor Role not found please add in database to assign")
    user = User.query.filter_by(email=email_id).first()
    if user:
        raise BadRequest("User is already availabe please login")
    else:
        try:
            ret = sign_up(signup_data, invitaion=True)
        except Exception as e:
            config.logging.error(f"{e}")
            raise BadRequest(f"{e}")

        try:
            new = User.query.filter_by(email=email_id).first()
            if not new:
                raise BadRequest("User Not created")
            add = Membership(
                user_id=new.id,
                brand_id=brand_id,
                role_id=role.id
            )
            log = BrandLog(id=uuid.uuid4(), user_id=brand.user_id, brand_id=brand_id,
                           message=f"{email_id} added in brand", created_at=get_time(), date=date.today())
            db.session.add(log)
            db.session.add(add)
            db.session.commit()
            return {"message": f"{email_id} Account Created successfully please login to check brand"}
        except Exception as e:
            config.logging.error(f"{e}")
            raise BadRequest(f"{e}")


def remove_user_from_brand(user_id, brand_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise BadRequest("User id is not valid please check again")

    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        raise BadRequest("Brand id is not valid please check again")

    available = Membership.query.filter(user_id == user_id).first()
    if available:
        if str(available.brand_id) == str(brand_id):
            try:
                db.session.delete(available)
                log = BrandLog(id=uuid.uuid4(), user_id=brand.user_id, brand_id=brand_id,
                               message=f"{user.email} removed from brand", created_at=get_time(), date=date.today())
                db.session.add(log)
                db.session.commit()
                return {"message": f"{user.email} Removed successfully from {brand.name}"}
            except Exception as e:
                raise BadRequest(f"Cannot Remove user due to {e}")
        else:
            raise BadRequest(
                "This user is not have access with given brand id")
    else:
        raise BadRequest("This user is not have any brand to remove")


def change_role_user_from_brand(user_id, brand_id, data):
    if "role" not in data:
        raise BadRequest("Please add role field in given data")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise BadRequest("User id is not valid please check again")

    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        raise BadRequest("Brand id is not valid please check again")
    available = Membership.query.filter(
        Membership.user_id == user_id, Membership.brand_id == brand_id).first()
    if not available:
        raise BadRequest("You are not assigned to this brand")
    role = RoleBrandUser.query.filter_by(name=data['role']).first()
    if not role:
        raise BadRequest(
            "Editor Role not found please add in database to assign")
    try:
        available.role_id = role.id
        log = BrandLog(id=uuid.uuid4(), user_id=brand.user_id, brand_id=brand_id,
                       message=f"{user.email} changed to {role.name}", created_at=get_time(), date=date.today())
        db.session.add(log)
        db.session.commit()
        return {"message": "Role or User is changed"}
    except Exception as e:
        config.logging.error(f"{e}")
        raise BadRequest(f"Error while changing the role.")
