import calendar
import time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.sqltypes import Boolean

from app.main import db


class BrandSocialAccounts(db.Model):
    __tablename__ = "brand_social_accounts"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    brand_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "brands.id"), nullable=False)
    name = db.Column(db.String, nullable=False)
    site_link = db.Column(db.String, nullable=True)
    username = db.Column(db.String, nullable=True)
    social_account_id = db.Column(db.String, nullable=True)
    access_key = db.Column(db.String, nullable=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.BIGINT, nullable=False,
                           default=calendar.timegm(time.gmtime()))
    updated_at = db.Column(db.BIGINT, nullable=False,
                           default=calendar.timegm(time.gmtime()))
    sharing_log = db.relationship(
        "SharingLog", backref="sharing_log", lazy=True)
