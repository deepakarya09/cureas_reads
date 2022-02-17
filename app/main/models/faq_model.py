import calendar
import time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.ext.mutable import MutableDict

from app.main import db

class FaqWidgit(db.Model):
    __tablename__ = "faq_widgit"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    brand_id = db.Column(UUID(as_uuid=True), db.ForeignKey("brands.id"), nullable=True)
    created_at = db.Column(db.BIGINT, nullable=False, default=calendar.timegm(time.gmtime()))
    data = db.Column(MutableDict.as_mutable(JSONB))
