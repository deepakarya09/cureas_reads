from sqlalchemy.dialects.postgresql import UUID
from app.main import db


class Token(db.Model):
    __tablename__ = "token"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=True)  
    used_by = db.Column(db.PickleType,nullable=True)
    count = db.Column(db.BIGINT)
    created_at = db.Column(db.BIGINT)
    updated_at = db.Column(db.BIGINT)