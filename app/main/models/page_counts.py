from sqlalchemy.dialects.postgresql import UUID

from app.main import db


class PageCount(db.Model):
    __tablename__ = "page_counts"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    page_count = db.Column(db.BIGINT, nullable=False, default=0)
