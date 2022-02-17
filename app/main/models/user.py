from sqlalchemy.dialects.postgresql import UUID

from app.main import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    role = db.Column(db.String(50), nullable=False, default="admin", )
    image_url = db.Column(db.String(500), nullable=True)
    verified = db.Column(db.Boolean,nullable=True,default=False)
    first_brand_exists = db.Column(db.Boolean, nullable=True, default=False)
    login_type = db.Column(db.String, nullable=True)
    user_creds = db.relationship("UserCredentials", uselist=False, backref="cred")
    rel_session = db.relationship("UserSession", backref="session",lazy=True)
    brand_article_content = db.relationship("BrandContent", backref="buac", lazy=True)
