import calendar
import time
from sqlalchemy.dialects.postgresql import UUID

from app.main import db


class StoryStats(db.Model):
    __tablename__ = "story_stats"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    story_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "brand_story.id"), nullable=False)
    brand_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "brands.id"), nullable=False)
    views = db.Column(db.Integer, default=0)
    ip = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=True)
    device = db.Column(db.String, nullable=True)
    created_at = db.Column(db.BIGINT, nullable=False,
                           default=calendar.timegm(time.gmtime()))
    date = db.Column(db.Date())
