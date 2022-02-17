from sqlalchemy.dialects.postgresql import UUID

from app.main import db


class ContentType(db.Model):
    __tablename__ = "content_types"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    ct = db.relationship("Content", backref="tp")
