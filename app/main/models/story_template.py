import calendar
import time
from sqlalchemy.dialects.postgresql import UUID
from app.main import db


class StoryTemplate(db.Model):
    __tablename__ = "story_templates"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    raw_html = db.Column(db.Text, nullable=False)
    block_count = db.Column(db.BIGINT, nullable=True)
    block_structure = db.Column(db.PickleType)
    created_at = db.Column(db.String(100), nullable=False,
                           default=calendar.timegm(time.gmtime()))
    updated_at = db.Column(db.String(100), nullable=False,
                           default=86400 + calendar.timegm(time.gmtime()))
    brand_story = db.relationship("BrandStory", backref="bs")
    thumbnail = db.Column(db.String(1000), nullable=True)
    draft_css = db.Column(db.String(1000), nullable=True)
    publish_css = db.Column(db.String(1000), nullable=True)
    category = db.Column(db.String(100))
    social_support = db.Column(db.PickleType)
