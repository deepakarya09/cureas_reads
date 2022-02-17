
from sqlalchemy.dialects.postgresql import UUID
from app.main import db


class WidgetsWithTags(db.Model):
    __tablename__ = "widget_with_tags"
    widget_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'widgets.id'), primary_key=True)
    tag_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'widget_tags.id'), primary_key=True)

    db.UniqueConstraint('widget_id', 'tag_id')
    db.relationship('Widget', uselist=False,
                    backref='widgetwithtag', lazy='dynamic')
    db.relationship('WidgetTag', uselist=False,
                    backref='widgetwithtag', lazy='dynamic')
