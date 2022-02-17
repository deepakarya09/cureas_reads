import calendar
import time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.sqltypes import Boolean

from app.main import db


class PageSeo(db.Model):
    __tablename__ = "page_seo"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    page_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "brand_pages.id"), nullable=False)
    icon = db.Column(db.String, nullable=True)
    title = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)
    page_link = db.Column(db.String, nullable=True)
    page_type = db.Column(db.String, nullable=True)
    facebook_publisher = db.Column(db.String, nullable=True)
    created_at = db.Column(db.BIGINT, nullable=False,
                           default=calendar.timegm(time.gmtime()))
    updated_at = db.Column(db.BIGINT, nullable=False,
                           default=calendar.timegm(time.gmtime()))
    banner_image = db.Column(db.String, nullable=True)
    twitter_id = db.Column(db.String, nullable=True)
