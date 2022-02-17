import calendar
import time
from sqlalchemy.dialects.postgresql import UUID
from app.main import db


class CssStyles(db.Model):
    __tablename__ = "css_styles"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    template_css_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "template_css_style.id"), nullable=False)
    class_names = db.Column(db.PickleType, nullable=True)
    active = db.Column(db.Boolean, nullable=True, default=False)
    description = db.Column(db.String(1000), nullable=True)
    mobile_thumbnail = db.Column(db.String(1000), nullable=True)
    css_link = db.Column(db.String(1000), nullable=False)
    desktop_thumbnail = db.Column(db.String(1000), nullable=True)
    created_at = db.Column(db.String(100), nullable=False,
                           default=calendar.timegm(time.gmtime()))
    updated_at = db.Column(db.String(100), nullable=False,
                           default=86400 + calendar.timegm(time.gmtime()))
