
import email
from app.main.models.token import Token
from app.main.services.user_registration_confirmation_mail import send_email, send_password_email
import calendar
from http import HTTPStatus
from itsdangerous import URLSafeTimedSerializer
import base64
import hashlib
import os
import time
import uuid
from flask import request
from google.auth.transport import requests
from google.oauth2 import id_token
from password_validation import PasswordPolicy
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden
from app.main import config, db
from app.main.models.user import User
from app.main.models.user_credentials import UserCredentials
from app.main.models.user_session import UserSession
from flask import current_app as cur_app
auth_s = URLSafeTimedSerializer(config.Config.SECRET_KEY, "auth")

policy = PasswordPolicy(uppercase=1, min_length=8, symbols=1)


def sign_up(data, invitaion):
    user = User.query.filter_by(email=data['email']).first()
    if user:
        if user.login_type == "system":
            raise BadRequest(
                f"{user.email} already exists. Please login with email and password.")
        if user.login_type == "google":
            raise BadRequest(
                f"{user.email} already exists. Please login with Google.")
    create_new_id = uuid.uuid4()
    try:
        if invitaion == False:
            if ("referral_code" in data) and (data["referral_code"] != None):
                valid = Token.query.filter_by(
                    code=data["referral_code"]).first()
                if valid:
                    if valid.count > 0:
                        if data["login_type"] == "system":
                            if "password" not in data.keys():
                                raise Unauthorized(
                                    "! Please enter the password")
                            if not policy.validate(data['password']):
                                raise Unauthorized(
                                    "! Password should contain atleast 8 characters with one uppercase letter, and one special character.")
                            if "first_name" in data.keys():
                                fname = data["first_name"]
                            else:
                                fname = ""
                            if "last_name" in data.keys():
                                lname = data["last_name"]
                            else:
                                lname = ""
                            if "image_url" in data.keys():
                                img = data["image_url"]
                            else:
                                img = "https://static.thenounproject.com/png/363633-200.png"

                            try:
                                user = User(id=create_new_id,
                                            first_name=fname,
                                            last_name=lname,
                                            email=data['email'],
                                            verified=False,
                                            login_type=data["login_type"],
                                            image_url=img)
                            except Exception as e:
                                config.logging.critical(
                                    f"! Failed to signup: {e}")
                                raise Exception(f"! Failed to signup {e}")
                            password = data['password']
                            salt = os.urandom(16)
                            key = hashlib.pbkdf2_hmac(
                                'sha256', password.encode('utf-8'), salt, 100000).hex()
                            salt = base64.b64encode(salt).decode()
                            password = salt + "$" + key
                            user_cred = UserCredentials(
                                password=password, cred=user)
                            db.session.add(user)
                            db.session.add(user_cred)
                            try:
                                valid.count = valid.count - 1
                                db.session.commit()
                            except Exception as e:
                                config.logging.critical(
                                    f"! Faild to use referral code: {e}")
                                raise BadRequest(
                                    f"! Faild to use referral code: {e}")
                            db.session.commit()
                            return response(user, token_build(user)), HTTPStatus.OK
                        elif data["login_type"] == "google":
                            verify_token(data['token'])
                            try:
                                use = User(id=create_new_id,
                                           first_name=data['first_name'],
                                           last_name=data['last_name'],
                                           email=data['email'],
                                           verified=True,
                                           role=data['role'] if 'role' in data else "admin",
                                           login_type=data["login_type"],
                                           image_url=data["image_url"])
                            except Exception as e:
                                config.logging.critical(
                                    f"Failed to signup using Google: {e}")
                                raise Exception(
                                    "! Failed to signup using Google. Please try again or try with email & password")
                            db.session.add(use)
                            db.session.commit()
                            try:
                                valid.count = valid.count - 1
                                db.session.commit()
                            except Exception as e:
                                config.logging.critical(
                                    f"! Faild to use referral code: {e}")
                                raise BadRequest(
                                    f"! Faild to use referral code: {e}")
                            return response(use, token_build(use)), HTTPStatus.OK
                    else:
                        raise BadRequest(
                            "Referral code is already used. Please use different code.")
                else:
                    raise BadRequest(
                        "Referral code is not valid. Please check again or try different code")
            else:
                raise BadRequest(
                    "Please enter referral code. If you don't have then contact with admin.")
        elif (invitaion == True):
            if data["login_type"] == "system":
                if "password" not in data.keys():
                    raise Unauthorized("! Please enter the password")
                if not policy.validate(data['password']):
                    raise Unauthorized(
                        "! Password should contain atleast 8 characters with one uppercase letter, and one special character.")
                if "first_name" in data.keys():
                    fname = data["first_name"]
                else:
                    fname = ""
                if "last_name" in data.keys():
                    lname = data["last_name"]
                else:
                    lname = ""
                if "image_url" in data.keys():
                    img = data["image_url"]
                else:
                    img = "https://static.thenounproject.com/png/363633-200.png"

                try:
                    user = User(id=create_new_id,
                                first_name=fname,
                                last_name=lname,
                                email=data['email'],
                                verified=True,
                                role=data['role'] if 'role' in data else "admin",
                                login_type=data["login_type"],
                                image_url=img,
                                first_brand_exists=True
                                )
                except Exception as e:
                    config.logging.critical(f"! Failed to signup: {e}")
                    raise Exception(f"! Failed to signup: {e}")
                password = data['password']
                salt = os.urandom(16)
                key = hashlib.pbkdf2_hmac(
                    'sha256', password.encode('utf-8'), salt, 100000).hex()
                salt = base64.b64encode(salt).decode()
                password = salt + "$" + key
                user_cred = UserCredentials(password=password, cred=user)
                db.session.add(user)
                db.session.add(user_cred)
                db.session.commit()
                return response(user, token_build(user))
            elif data["login_type"] == "google":
                verify_token(data['token'])
                try:
                    use = User(id=create_new_id,
                               first_name=data['first_name'],
                               last_name=data['last_name'],
                               email=data['email'],
                               verified=True,
                               role=data['role'] if 'role' in data else "admin",
                               first_brand_exists=True,
                               login_type=data["login_type"],
                               image_url=data["image_url"])
                except Exception as e:
                    config.logging.critical(
                        f"! Failed to signup with invited link : {e}")
                    raise Exception(
                        f"! Failed to signup with invited link : {e}")
                db.session.add(use)
                db.session.commit()
                return response(use, token_build(use))
    except Exception as e:
        raise BadRequest(f"{e.description}")


def token_build(user):
    if user.login_type == "system":
        if user.verified == False:
            if user.first_brand_exists == False:
                send_email(user.email)
    sub_key = os.urandom(16)
    session_uuid = uuid.uuid4()
    userId = str(user.id)
    sessionId = str(session_uuid)

    part1 = base64.b64encode(sessionId.encode()).decode()
    part2 = hashlib.sha512((userId[::-1]).encode()).hexdigest()
    part3 = base64.b64encode(sub_key).decode()

    token = part1 + "." + part2 + "." + part3
    try:
        create_session = UserSession(session_id=session_uuid, token=token,
                                     expires_at=calendar.timegm(time.gmtime()) + 86400, session=user)

        db.session.add(create_session)
        db.session.commit()
    except Exception as e:
        config.logging.critical(f"! Failed to generate user token : {e}")
        raise BadRequest(f"! Failed to generate user token : {e}")
    try:
        return {
            "id": user.id,
            "token": token,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "image_url": user.image_url,
            "email": user.email,
            "verified": user.verified,
            "login_type": user.login_type,
            "role": user.role,
            "first_brand_exists": user.first_brand_exists,
            "session_id": sessionId
        }
    except Exception as e:
        config.logging.critical(f"! Failed to generate user token : {e}")
        raise BadRequest("! Failed to generate user token")


def sign_in(data):
    user = User.query.filter_by(email=data['email']).first()
    if data['login_type'] != 'system':
        if data['login_type'] == "google":
            verify_token(data['token'])
        else:
            # apple login verification #
            pass
        return response(user, token_build(user))
    if not "password" in data:
        raise BadRequest("Please enter password!")
    password = data['password']

    if not policy.validate(data['password']):
        raise BadRequest("Wrong password. ! Please enter valid password.")

    if not user:
        raise BadRequest("You are not a valid user. Please create account.")

    userCred = UserCredentials.query.filter_by(id=user.id).first()
    salt, hash_password = userCred.password.split("$")
    salt = salt.encode()
    salt = base64.b64decode(salt)
    key = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt, 100000).hex()

    if key != hash_password:
        raise Unauthorized("Wrong password. ! Please enter valid password.")
    return token_build(user)


def logout():
    headers = request.headers
    bearer = headers.get('Authorization')
    if not bearer:
        raise Forbidden("User is not authorized please login before logout")
    token = bearer.split()[1]
    sess = UserSession.query.filter_by(token=token).first()
    if not sess:
        raise Forbidden("Invalid user please try again.")
    db.session.delete(sess)
    db.session.commit()
    return {"message": "User logged out successfully"}, HTTPStatus.OK


def verify_token(token):
    try:
        info = id_token.verify_oauth2_token(token, requests.Request())
        if info['aud'] not in [cur_app.config['EXTENSION_CLIENT_ID_PRODUCTION'], cur_app.config["CLIENT_ID_PRODUCTION"], cur_app.config['CLIENT_ID_DEVELOPMENT'], cur_app.config['EXTENSION_CLIENT_ID_DEVELOPMENT']]:
            raise BadRequest(
                "Google token verification failed, Please Login again with google")
    except ValueError as e:
        config.logging.critical(f"{e}")
        raise BadRequest(
            "Google token verification failed, Please Login again with google")


def response(user, token_data):
    # NOT used join query because it heavy in processing and takes more time
    user.token = token_data["token"]
    user.session_id = token_data["session_id"]
    return user


def login(data):
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        config.logging.warning(
            f"{data['email']} not in our system: Please create account")
        raise BadRequest(
            f"{data['email']} not in our system: Please create account")

    if data["login_type"] != 'system':
        if data["login_type"] == "google":
            verify_token(data['token'])
        return response(user, token_build(user))

    if data['login_type'] == "system":
        if str(user.login_type) == "google":
            raise BadRequest(
                "Account already exists, please use google to login.")
        if not "password" in data:
            raise BadRequest("Please enter password!")
        password = data['password']
        if not policy.validate(password):
            raise BadRequest("! Password is not valid.")
        try:
            userCred = UserCredentials.query.filter_by(id=user.id).first()
            salt, hash_password = userCred.password.split("$")
            salt = salt.encode()
            salt = base64.b64decode(salt)
            key = hashlib.pbkdf2_hmac(
                'sha256', password.encode('utf-8'), salt, 100000).hex()
            if key != hash_password:
                raise Unauthorized("! Password doesn't match.")
            return token_build(user)
        except:
            raise BadRequest(
                "Not able to signin at this movement. Please check email and password")


def forget_password_notification(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        config.logging.warning(
            f"{email} not in our system: Please create account")
        raise BadRequest(f"{email} not in our system: Please create account")
    if user.login_type != 'system':
        raise BadRequest(
            f"You are registered with Google please login with that.")
    try:
        send_password_email(email)
        return {"message": "Change Password notification sended on your email please confirm"}, HTTPStatus.OK
    except:
        raise BadRequest("Not able to send email for changing password")


def change_password(data, confirm_code):
    try:
        value = auth_s.loads(confirm_code, max_age=172800)
    except Exception as e:
        raise BadRequest(
            f"confirmation link not valid or expired please resend")
    if "email" not in value:
        raise BadRequest("Confirmation Link is not valid")
    email_id = value["email"]
    user = User.query.filter_by(email=email_id).first()
    if not user:
        config.logging.warning(
            f"{email_id} not in our system: Please create account")
    password = data['password']
    confirm_password = data['confirm_password']
    if not policy.validate(password):
        raise BadRequest("! Password is not valid.")
    if password != confirm_password:
        raise BadRequest("! Password is not match with confirm password.")
    try:
        userCred = UserCredentials.query.filter_by(id=user.id).first()
        if not userCred:
            raise BadRequest(
                f"Your old password dosen't exists please contact to admin")
        salt, hash_password = userCred.password.split("$")
        salt = salt.encode()
        salt = base64.b64decode(salt)
        key = hashlib.pbkdf2_hmac(
            'sha256', password.encode('utf-8'), salt, 100000).hex()
        if key == hash_password:
            raise BadRequest(
                "! This is your old password please login or try new password.")
        else:
            salt = os.urandom(16)
            key = hashlib.pbkdf2_hmac(
                'sha256', password.encode('utf-8'), salt, 100000).hex()
            salt = base64.b64encode(salt).decode()
            new_password = salt + "$" + key
            userCred.password = new_password
            db.session.commit()
        return {"message": "Your password is changed please login"}, HTTPStatus.OK
    except Exception as e:
        config.logging.warning(
            f"Not able to change password: {e}")
        raise BadRequest(
            f"Not able to change password: {e}")
