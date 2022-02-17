import calendar
import time
from sqlalchemy.dialects.postgresql import UUID

from app.main import db
from app.main.models.content_tags import contentTags
from app.main.models.content_types import ContentType


class Content(db.Model):
    __tablename__ = "contents"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    title = db.Column(db.String(1000))
    description = db.Column(db.String(1000))
    site_link = db.Column(db.String(1000),)
    canonical_link = db.Column(db.String(1000), nullable=False, unique=True)
    image_link = db.Column(db.String(1000))
    cdn_image_link = db.Column(db.String(1000))
    source_id = db.Column(UUID(as_uuid=True), db.ForeignKey("sources.id"), nullable=True)
    content_type_id = db.Column(UUID(as_uuid=True), db.ForeignKey("content_types.id"), nullable=True)
    status = db.Column(db.String(30), default='DRAFT')
    type = db.Column(db.String(40))
    country = db.Column(db.String(40), default='US')
    modified_at = db.Column(db.BIGINT, nullable=False, default=calendar.timegm(time.gmtime()))
    created_at = db.Column(db.BIGINT, nullable=False, default=calendar.timegm(time.gmtime()))
    site_name = db.Column(db.String(200))
    con_conn = db.relationship("Tag", secondary=contentTags, backref=db.backref("cont", lazy='dynamic'))
    used = db.Column(db.Boolean, default=False)
    counter = db.Column(db.Integer, nullable=True)
    expired_at = db.Column(db.BIGINT, default=86400 + calendar.timegm(time.gmtime()))
