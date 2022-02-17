import calendar
import time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.sqltypes import Boolean
from datetime import date
from app.main import db


class SharingLog(db.Model):
    __tablename__ = "sharing_log"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    story_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "brand_story.id"), nullable=False)
    social_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "brand_social_accounts.id"), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "users.id"), nullable=False)
    brand_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "brands.id"), nullable=False
    )
    schedule_time = db.Column(db.BIGINT, nullable=False)
    success = db.Column(db.Boolean, nullable=False, default=False)
    deleted = db.Column(db.Boolean, default=False)
    schedule = db.Column(db.Boolean, nullable=False, default=False)
    sharing_status = db.Column(db.String, nullable=True)
    caption = db.Column(db.String, nullable=True)
    image_link = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    retry_count = db.Column(db.BIGINT, nullable=False, default=0)
    posting_id = db.Column(db.String, nullable=True)
    date = db.Column(db.Date(), default=date.today())
    created_at = db.Column(db.BIGINT, nullable=False,
                           default=calendar.timegm(time.gmtime()))
    updated_at = db.Column(db.BIGINT, nullable=False,
                           default=calendar.timegm(time.gmtime()))
