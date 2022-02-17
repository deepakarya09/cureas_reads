from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.mutable import MutableDict

from app.main import db


class Widget(db.Model):
    __tablename__ = "widgets"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    raw_html = db.Column(db.Text)
    default_data = db.Column(MutableDict.as_mutable(JSONB))
    created_at = db.Column(db.BIGINT, nullable=False)
    updated_at = db.Column(db.BIGINT, nullable=True)
    thumbnail = db.Column(db.String(1000), nullable=True)
    category = db.Column(db.String(100))
    type = db.Column(db.String(50), nullable=True)
