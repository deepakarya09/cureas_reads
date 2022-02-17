import calendar
import time
from sqlalchemy.dialects.postgresql import UUID
from app.main import db


class StoryEditors(db.Model):
    __tablename__ = "story_editors"
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'users.id'), primary_key=True)
    story_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'brand_story.id'), primary_key=True)
    created_at = db.Column(db.BIGINT, nullable=False,
                           default=calendar.timegm(time.gmtime()))
    updated_at = db.Column(db.BIGINT, nullable=False,
                           default=calendar.timegm(time.gmtime()))

    db.UniqueConstraint('user_id', 'story_id')
    db.relationship('User', uselist=False,
                    backref='storyeditors', lazy='dynamic')
    db.relationship('BrandStory', uselist=False,
                    backref='storyeditors', lazy='dynamic')
