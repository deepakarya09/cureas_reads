from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.ext.mutable import MutableDict, MutableList
from app.main.models.story_data import StoryData
from app.main.models.template_creation import Template
from app.main.models.page_data import PageData
from app.main import db


class BrandStory(db.Model):
    __tablename__ = "brand_story"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    brand_id = db.Column(UUID(as_uuid=True),
                         db.ForeignKey("brands.id"), nullable=True)
    story_name = db.Column(db.String, nullable=True)
    template_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "story_templates.id"), nullable=True)
    template_raw_html = db.Column(db.Text,  nullable=True, default='')
    total_block_count = db.Column(db.Integer)
    filled_block_count = db.Column(db.Integer)
    story_link = db.Column(db.String)
    status = db.Column(db.Enum("DRAFT", "PUBLISHED", "SCHEDULED",
                       name="branding_story_status"), server_default="DRAFT")
    published_at = db.Column(db.BIGINT, nullable=True)
    created_at = db.Column(db.BIGINT, nullable=False)
    updated_at = db.Column(db.BIGINT, nullable=True)
    story_data = db.relationship(
        "StoryData", backref="story_data", order_by=StoryData.block_no, lazy=True)
    category = db.Column(db.String(100), nullable=True)
    active = db.Column(db.Boolean, default=False)
    thumbnail_image = db.Column(db.String)
    story_seo = db.relationship(
        "StorySeo", uselist=False, backref="storyseo", lazy=True)
    # story_share = db.relationship(
    #     "StoryShare", uselist=False, backref="story_share", lazy=True)
