from app.main.models.brands import Brand
from re import TEMPLATE
from werkzeug.exceptions import BadRequest
from flask import render_template
from app.main.models.user import User
from app.main import config, create_app, db
from flask_mail import Mail, Message
import uuid
import base64
from itsdangerous import URLSafeTimedSerializer
from flask import current_app as cur_app

auth_s = URLSafeTimedSerializer(config.Config.SECRET_KEY, "auth")


app = create_app('prod')
mail = Mail(app)


def send_email(email):
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            BadRequest("user not found")
        email = email
        uui = str(user.id)
        message_bytes = uui.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        tok = base64_bytes.decode('ascii')
        token = f"{tok}_{uuid.uuid4()}"
        # token = uui.encode('ascii')
        msg = Message('Confirm Email', sender='admin@pwc.com',
                      recipients=[email])
        link = f"{cur_app.config['EMAIL_VERIFICATION_DOMAIN']}{token}"
        msg.body = 'Your link is {}'.format(link)
        msg.html = render_template('email_1.html', elink=link)
        mail.send(msg)
        return {
            "message": "sended"
        }
    except Exception as e:
        raise BadRequest(f"Message not Sended due to {e}")


def send_confirmation_email(email, brand_id):
    try:
        brand = Brand.query.filter_by(id=brand_id).first()
        if not brand:
            raise BadRequest(
                "Brand Not found in email varification with given brand id")
        invited_user = User.query.filter_by(id=brand.user_id).first()
        if not invited_user:
            raise BadRequest("Brand have not any admin")
        link_for_invitation = auth_s.dumps(
            {"email": email, "brand_id": brand_id})
        msg = Message('Confirm Brand', sender='admin@pwc.com',
                      recipients=[email])
        link = f"{cur_app.config['EMAIL_INVITATION']}{link_for_invitation}"
        msg.body = 'Your link is {}'.format(link)
        msg.html = render_template(
            'email_2.html', elink=link, logo=brand.white_theme_logo, name=brand.name, invited_by=invited_user.email)
        mail.send(msg)
        return f"Invitation email Sended successfully to {email}"
    except Exception as e:
        raise BadRequest(f"Message not Sended due to {e}")


def confirm_email(token):
    if token == None:
        BadRequest("Please enter token")
    tok = token.split('_')
    toke = tok[0]
    try:
        base64_bytes = toke.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        userid = message_bytes.decode('ascii')
    except Exception as e:
        raise BadRequest("URL is not valid please try again")
    try:
        uuid.UUID(userid)
    except Exception as e:
        config.logging.warning(f"api: token id : Invalid Submission Id. {e}")
        raise BadRequest("This token id not valid.")
    user = User.query.filter_by(id=userid).first()
    if not user:
        raise BadRequest("URL is not valid")
    user.verified = True
    db.session.commit()
    if user.verified == True:
        return {
            "message": "Your account is already verified"
        }
    return {
        "message": "verified"
    }


def send_password_email(email):
    try:
        link_for_invitation = auth_s.dumps({"email": email})
        msg = Message('Change password', sender='admin@pwc.com',
                      recipients=[email])
        link = f"{cur_app.config['EMAIL_CHANGE_PASSWORD']}{link_for_invitation}"
        msg.body = 'Your link is {}'.format(link)
        msg.html = render_template('email_3.html', elink=link)
        mail.send(msg)
        return f"Password Changing email Sended successfully to {email}"
    except Exception as e:
        raise BadRequest(f"Message not Sended due to {e}")
