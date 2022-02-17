import calendar
import time

from sqlalchemy.dialects.postgresql import UUID

from app.main import db


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    worker_id = db.Column(db.String(100))
    worker_type = db.Column(db.String(50))
    submitted_article_count = db.Column(db.Integer, default=0)
    confirmation_code = db.Column(db.String)
    created_at = db.Column(db.BIGINT, nullable=False, default=calendar.timegm(time.gmtime()))
    submitted_at = db.Column(db.BIGINT, nullable=True)
    modified_at = db.Column(db.BIGINT, nullable=True)
    sub_articles = db.relationship("SubmittedArticle", backref="sub_article")
    payment_status = db.Column(db.Boolean, default=False)
    payment_status_update_at = db.Column(db.BIGINT, nullable=True)
