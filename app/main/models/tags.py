from sqlalchemy.dialects.postgresql import UUID
from app.main import db
from app.main.models.content_tags import contentTags
from app.main.models.submitted_articles import submitted_article_tags


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    tag_con = db.relationship("Content", secondary=contentTags, backref=db.backref("tag", lazy='dynamic'))
    sub_article_conn = db.relationship("SubmittedArticle", secondary=submitted_article_tags,
                                       backref=db.backref("sub_tag", lazy='dynamic'))