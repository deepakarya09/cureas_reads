from sqlalchemy.dialects.postgresql import UUID

from app.main import db

submitted_article_tags = db.Table("submitted_article_tags", db.Model.metadata,
                                  db.Column("submitted_article_id", UUID(as_uuid=True),
                                            db.ForeignKey("submitted_articles.id")),
                                  db.Column("tag_id", UUID(as_uuid=True), db.ForeignKey("tags.id")))


class SubmittedArticle(db.Model):
    __tablename__ = "submitted_articles"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    title = db.Column(db.String(1000))
    description = db.Column(db.String(1000))
    site_link = db.Column(db.String(1000))
    canonical_link = db.Column(db.String(1000), nullable=False)
    image_link = db.Column(db.String(1000))
    type = db.Column(db.String(40), nullable=True)
    submission_id = db.Column(UUID(as_uuid=True), db.ForeignKey("submissions.id"), nullable=True)
    country = db.Column(db.String(30))
    city = db.Column(db.String(100), nullable=True)
    user_ip = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(30), default='APPROVED')
    created_at = db.Column(db.BIGINT, nullable=False)
    site_name = db.Column(db.String(200))
    tag_multi_con = db.relationship("Tag", secondary=submitted_article_tags, backref=db.backref("art", lazy='dynamic'))
    user_agent = db.Column(db.String(200), nullable=True)
    sequence_number = db.Column(db.Integer)
