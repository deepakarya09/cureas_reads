from sqlalchemy.dialects.postgresql import UUID
from app.main import db


class UserSession(db.Model):
    __tablename__ = "user_sessions"

    session_id = db.Column(UUID(as_uuid=True), primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"))
    token = db.Column(db.String(256), nullable=False)
    expires_at = db.Column(db.BIGINT, nullable=False)
