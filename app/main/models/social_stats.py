import calendar
import time
from datetime import date
from sqlalchemy.dialects.postgresql import UUID
from app.main.models.user import User
from app.main.models.brands import Brand

from app.main import db


class SocialStats(db.Model):
    __tablename__ = "social_stats"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    social_id = db.Column(UUID(as_uuid=True),
                          db.ForeignKey("brand_social_accounts.id"), nullable=True)
    brand_id = db.Column(UUID(as_uuid=True),
                         db.ForeignKey("brands.id"), nullable=True)
    sharing_id = db.Column(UUID(as_uuid=True),
                           db.ForeignKey("sharing_log.id"), nullable=True)
    likes = db.Column(db.BIGINT, default=0)
    comments = db.Column(db.BIGINT, default=0)
    views = db.Column(db.BIGINT, default=0)
    interaction = db.Column(db.BIGINT, default=0)
    account_type = db.Column(db.String)
    date = db.Column(db.Date(), default=date.today())
    created_at = db.Column(db.BIGINT, nullable=False,
                           default=calendar.timegm(time.gmtime()))
