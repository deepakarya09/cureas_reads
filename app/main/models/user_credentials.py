from sqlalchemy.dialects.postgresql import UUID
from app.main import db


class UserCredentials(db.Model):
    __tablename__ = "user_credentials"
    id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), primary_key=True)
    password = db.Column(db.String(256))
