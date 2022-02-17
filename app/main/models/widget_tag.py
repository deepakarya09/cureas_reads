from sqlalchemy.dialects.postgresql import UUID
from app.main import db


class WidgetTag(db.Model):
    __tablename__ = "widget_tags"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
