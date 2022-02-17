import calendar
import time
from sqlalchemy.dialects.postgresql import UUID
from app.main import db


class RoleBrandUser(db.Model):
    __tablename__ = "rolebranduser"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.BIGINT, nullable=False, default=calendar.timegm(time.gmtime()))