
import calendar
import time
from sqlalchemy.dialects.postgresql import UUID
from app.main import db


class Membership(db.Model):
    __tablename__ = "membership"
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'users.id'), primary_key=True)
    brand_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'brands.id'), primary_key=True)
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'rolebranduser.id'), primary_key=True)
    created_at = db.Column(db.BIGINT,
                           default=calendar.timegm(time.gmtime()))
    active = db.Column(db.Boolean, nullable=True, default=False)

    db.UniqueConstraint('user_id', 'brand_id', 'role_id')
    db.relationship('User', uselist=False,
                    backref='memberships', lazy='dynamic')
    db.relationship('Brand', uselist=False,
                    backref='memberships', lazy='dynamic')
    db.relationship('RoleBrandUser', uselist=False,
                    backref='memberships', lazy='dynamic')
