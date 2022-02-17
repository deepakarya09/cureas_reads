import calendar
import time
from sqlalchemy.dialects.postgresql import UUID

from app.main import db


class GeneratedPages(db.Model):
    __tablename__ = "generated_pages"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    page_name = db.Column(db.String(40), nullable=False)
    layout_name = db.Column(db.String(40), nullable=False)
    created_at = db.Column(db.BIGINT, nullable=False, default=calendar.timegm(time.gmtime()))
    expires_at = db.Column(db.BIGINT, nullable=False, default=86400+calendar.timegm(time.gmtime()))
    storage_location = db.Column(db.String(40), nullable=True)
    country = db.Column(db.String(10), nullable=False)
    published_at = db.Column(db.BIGINT, nullable=True)