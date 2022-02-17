from sqlalchemy.dialects.postgresql import UUID

from app.main import db


class Source(db.Model):
    __tablename__ = "sources"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    website_link = db.Column(db.String(500), nullable=False)
    stream_link = db.Column(db.String(500), nullable=False)
    stream_type = db.Column(db.String(50), nullable=False, default="RSS FEED")
    region = db.Column(db.PickleType)
    content_type = db.Column(db.PickleType)
    polling_interval = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.BIGINT, nullable=False)
    updated_at = db.Column(db.BIGINT, nullable=False)
    content = db.relationship("Content", backref="src")
