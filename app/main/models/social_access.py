
from sqlalchemy.dialects.postgresql import UUID
from app.main import db


class SocialAccess(db.Model):
    __tablename__ = "social_access"
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'users.id'), primary_key=True)
    brand_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'brands.id'), primary_key=True)
    social_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'brand_social_accounts.id'), primary_key=True)
    active = db.Column(db.Boolean, nullable=True, default=False)

    db.UniqueConstraint('user_id', 'brand_id', 'social_id')
    db.relationship('User', uselist=False,
                    backref='socialaccess', lazy='dynamic')
    db.relationship('Brand', uselist=False,
                    backref='socialaccess', lazy='dynamic')
    db.relationship('BrandSocialAccounts', uselist=False,
                    backref='socialaccess', lazy='dynamic')
