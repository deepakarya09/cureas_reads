from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.sqltypes import Boolean

from app.main import db


class StoryData(db.Model):
    __tablename__ = "story_data"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    story_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "brand_story.id"), nullable=True)
    block_no = db.Column(db.Integer, nullable=False)
    widget_name = db.Column(db.String, nullable=False)
    widget_type = db.Column(db.String, nullable=True)
    widget_page = db.Column(db.Text, nullable=False)
    updated = db.Column(Boolean, unique=False, default=False)
