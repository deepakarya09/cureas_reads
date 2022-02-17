import calendar
import time
from sqlalchemy.dialects.postgresql import UUID
from app.main.models.user import User
from app.main.models.brands import Brand

from app.main import db


class BrandLog(db.Model):
    __tablename__ = "brand_log"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    message = db.Column(db.String(1000))
    user_id = db.Column(UUID(as_uuid=True),
                        db.ForeignKey("users.id"), nullable=True)
    brand_id = db.Column(UUID(as_uuid=True),
                         db.ForeignKey("brands.id"), nullable=True)
    created_at = db.Column(db.BIGINT, nullable=False,
                           default=calendar.timegm(time.gmtime()))
    date = db.Column(db.Date())
