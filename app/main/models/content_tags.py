from sqlalchemy.dialects.postgresql import UUID
from app.main import db


contentTags = db.Table("content_tags", db.Model.metadata,
                       db.Column("content_id", UUID(as_uuid=True), db.ForeignKey("contents.id")),
                       db.Column("tag_id", UUID(as_uuid=True), db.ForeignKey("tags.id")))


