from app.main.models.email_subscribers import EmailSubs
import uuid
from werkzeug.exceptions import BadRequest
from app.main import config
from app.main import db
from app.main.models.brands import Brand

def collect_subscriber(data):
    email = data['email']
    fqdn = data['fqdn']
    brand = Brand.query.filter_by(fqdn=fqdn).first()
    if not brand:
        raise BadRequest("Brand not available in database. Please check again")
    check = EmailSubs.query.filter_by(email=email).first()
    if check:
        if str(check.brand_id) == str(brand.id):
            raise BadRequest(f"Your email {email} is already subscribed with brand {brand.name}")
    try:
        collect = EmailSubs(
            id = uuid.uuid4(),
            email = email,
            brand_id = brand.id
        )
        db.session.add(collect)
        db.session.commit()
        return {
            "message":f"Thank-you for subscribing brand {brand.name}"
        }
    except Exception as e:
        raise BadRequest(f"Error in subscribe {e}")

def all_subs_by_brand(brand_id):
    try:
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(
            f"api: get brand by brand id : Invalid Submission Id. {e}")
        raise BadRequest("Brand id is not valid.") 
    subs = EmailSubs.query.filter_by(brand_id=brand_id).all()
    return {"items":subs}

def remove_subscriber(data):
    email = data['email']
    fqdn = data['fqdn']
    brand = Brand.query.filter_by(fqdn=fqdn).first()
    if not brand:
        raise BadRequest("Brand not available in database. Please check again.")
    check = EmailSubs.query.filter_by(email=email).first()
    if check:
        if str(check.brand_id) == str(brand.id):
            try:
                db.session.delete(check)
                db.session.commit()
                return {"message":f"Your email {email} is succesfully unsubscribe from {brand.name}"}
            except Exception as e:
                raise BadRequest(f"{e}")
    raise BadRequest(f"You are not a subscriber of brand {brand.name}. Please subscribe first")