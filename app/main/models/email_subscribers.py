import calendar
import time
from sqlalchemy.dialects.postgresql import UUID

from app.main import db

class EmailSubs(db.Model):
    __tablename__ = "emailsubs"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    email = db.Column(db.String(1000))
    brand_id = db.Column(UUID(as_uuid=True), db.ForeignKey("brands.id"), nullable=True)
    subscribe_at = db.Column(db.BIGINT, nullable=False, default=calendar.timegm(time.gmtime()))