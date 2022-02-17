import calendar
import time
from sqlalchemy.dialects.postgresql import UUID
from app.main import db

class PageEditors(db.Model):
    __tablename__ = "page_editors"
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), primary_key=True)
    page_id = db.Column(UUID(as_uuid=True), db.ForeignKey('brand_pages.id'), primary_key=True)
    created_at = db.Column(db.BIGINT, nullable=False, default=calendar.timegm(time.gmtime()))
    updated_at = db.Column(db.BIGINT, nullable=False, default=calendar.timegm(time.gmtime()))

    db.UniqueConstraint('user_id', 'page_id')
    db.relationship('User', uselist=False, backref='pageeditors', lazy='dynamic')
    db.relationship('BrandPages', uselist=False, backref='pageeditors', lazy='dynamic')