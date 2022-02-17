import calendar
import time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.ext.mutable import MutableDict

from app.main import db

class ssl_cert_generation(db.Model): 
    __tablename__ = "ssl_cert_generation"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    brand_id = db.Column(UUID(as_uuid=True), db.ForeignKey("brands.id"), nullable=True)
    fqdn = db.Column(db.String(100), nullable=True, unique=True)
    fqdn_expiry_at =  db.Column(db.BIGINT, nullable=True)
    fqdn_created_at = db.Column(db.BIGINT, nullable=True)
    failure_reason = db.Column(db.String(1000), nullable=True)
    retry_count = db.Column(db.Integer, nullable=False)
    ssl_status =  db.Column(db.Boolean, default=False)
    old_fqdn = db.Column(db.String(1000), nullable=True)
    ssl_in_use =  db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.BIGINT, nullable=False)
    created_at = db.Column(db.BIGINT, nullable=False, default=calendar.timegm(time.gmtime()))

