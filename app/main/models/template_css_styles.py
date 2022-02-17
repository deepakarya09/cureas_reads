import calendar
import time
from sqlalchemy.dialects.postgresql import UUID
from app.main import db


class TemplateCssStyles(db.Model):
    __tablename__ = "template_css_style"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    widget_count = db.Column(db.BIGINT, nullable=True)
    description = db.Column(db.String(1000), nullable=True)
    created_at = db.Column(db.String(100), nullable=False,
                           default=calendar.timegm(time.gmtime()))
    updated_at = db.Column(db.String(100), nullable=False,
                           default=86400 + calendar.timegm(time.gmtime()))
