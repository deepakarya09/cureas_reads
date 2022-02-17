from datetime import date, timedelta
import uuid
from http import HTTPStatus
from werkzeug.exceptions import BadRequest
from app.main import db, config
from app.main.models.brands import Brand
from app.main.models.brand_log import BrandLog
import sqlalchemy as sq

from app.main.models.user import User


def get_brand_logs(brand_id):
    try:
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(
            f"Api: Post article : Invalid submission - brand Id: {brand_id}.")
        raise BadRequest(f"This {brand_id} - Brand id is not valid.")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        raise BadRequest(
            "Brand not available in database. Please check brand id.")
    seven_days = date.today() - timedelta(days=7)
    data = BrandLog.query.filter(
        BrandLog.brand_id == brand_id).filter(BrandLog.date >= seven_days).order_by(BrandLog.created_at.desc()).all()
    items = []
    for i in data:
        user = User.query.filter(User.id == i.user_id).first()
        d = {
            "user": user,
            "id": i.id,
            "message": i.message,
            "brand_id": i.brand_id,
            "created_at": i.created_at,
            "date": i.date
        }
        items.append(d)

    return {"items": items}, HTTPStatus.OK
