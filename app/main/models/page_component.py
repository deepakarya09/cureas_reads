import calendar
import time
from sqlalchemy.dialects.postgresql import UUID

from app.main import db


class PageComponent(db.Model):
    __tablename__ = "page_component"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    data = db.Column(db.Text, nullable=False)
    name = db.Column(db.String)
    category = db.Column(db.String)
    active = db.Column(db.Boolean, nullable=True, default=False)
    created_at = db.Column(db.BIGINT, nullable=False, default=calendar.timegm(time.gmtime()))
    updated_at = db.Column(db.BIGINT, nullable=False, default=calendar.timegm(time.gmtime()))

