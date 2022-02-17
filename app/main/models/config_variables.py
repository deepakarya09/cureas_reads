from sqlalchemy.dialects.postgresql import UUID
from app.main import db


class ConfigVariables(db.Model):
    __tablename__ = "configVariables"

    key = db.Column(db.String(500), primary_key=True)
    value = db.Column(db.String(100))
