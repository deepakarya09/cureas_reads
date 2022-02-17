import calendar
import time
from sqlalchemy.dialects.postgresql import UUID

from app.main import db

class PricingWidgit(db.Model):
    __tablename__ = "pricing_widgit"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    brand_id = db.Column(UUID(as_uuid=True), db.ForeignKey("brands.id"), nullable=True)
    created_at = db.Column(db.BIGINT, nullable=False, default=calendar.timegm(time.gmtime()))
    title = db.Column(db.String, nullable=True)
    subtitle = db.Column(db.String, nullable=True)
    point_1 = db.Column(db.String, nullable=True)
    point_2 = db.Column(db.String, nullable=True)
    point_3 = db.Column(db.String, nullable=True)
    point_4 = db.Column(db.String, nullable=True)
    point_5 = db.Column(db.String, nullable=True)
    point_6 = db.Column(db.String, nullable=True)
    point_7 = db.Column(db.String, nullable=True)
    point_8 = db.Column(db.String, nullable=True)
    point_9 = db.Column(db.String, nullable=True)
    point_10 = db.Column(db.String, nullable=True)
    button = db.Column(db.JSON, nullable=True)