import calendar
import time
from sqlalchemy.dialects.postgresql import UUID
from app.main.models.user import User
from app.main.models.brands import Brand

from app.main import db


class BrandContent(db.Model):
    __tablename__ = "brand_articles"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    title = db.Column(db.String(1000))
    description = db.Column(db.String(1000))
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=True)
    brand_id = db.Column(UUID(as_uuid=True), db.ForeignKey("brands.id"), nullable=True)
    canonical_link = db.Column(db.String(1000), nullable=False)
    image_link = db.Column(db.String(1000))
    content_type = db.Column(db.String(40))
    favicon_icon_link = db.Column(db.String(1000), nullable=True)
    updated_at = db.Column(db.BIGINT, nullable=False, default=calendar.timegm(time.gmtime()))
    created_at = db.Column(db.BIGINT, nullable=False, default=calendar.timegm(time.gmtime()))
    site_name = db.Column(db.String(200))
    tags = db.Column(db.PickleType,nullable=True)
