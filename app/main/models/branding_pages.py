from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.ext.mutable import MutableDict, MutableList
from app.main.models.template_creation import Template
from app.main.models.page_data import PageData
from app.main import db


class BrandPages(db.Model):
    __tablename__ = "brand_pages"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    brand_id = db.Column(UUID(as_uuid=True),
                         db.ForeignKey("brands.id"), nullable=True)
    page_name = db.Column(db.String, nullable=True)
    template_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "templates.id"), nullable=True)
    template_raw_html = db.Column(db.Text,  nullable=True, default='')
    total_block_count = db.Column(db.Integer)
    filled_block_count = db.Column(db.Integer)
    cdn_html_page_link = db.Column(db.String)
    status = db.Column(db.Enum("DRAFT", "PUBLISHED", "SCHEDULED",
                       name="branding_page_status"), server_default="DRAFT")
    published_at = db.Column(db.BIGINT, nullable=True)
    created_at = db.Column(db.BIGINT, nullable=False)
    updated_at = db.Column(db.BIGINT, nullable=True)
    page_data = db.relationship(
        "PageData", backref="page_data", order_by=PageData.block_no, lazy=True)
    category = db.Column(db.String(100), nullable=True)
    active = db.Column(db.Boolean, nullable=True)
    thumbnail_image = db.Column(db.String)
    page_seo = db.relationship(
        "PageSeo", uselist=False, backref="pageseo", lazy=True)
