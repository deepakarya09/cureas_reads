from sqlalchemy.dialects.postgresql import UUID
from app.main import db


class Brand(db.Model):
    __tablename__ = "brands"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "users.id"), nullable=False)
    site_url = db.Column(db.String(1000), nullable=True, unique=True)
    fqdn = db.Column(db.String(100), nullable=True, unique=True)
    default_fqdn = db.Column(db.String(100), nullable=True, unique=True)
    description = db.Column(db.String(1000), nullable=True)
    facebook_url = db.Column(db.String(1000), nullable=True)
    twitter_url = db.Column(db.String(1000), nullable=True)
    instagram_url = db.Column(db.String(1000), nullable=True)
    white_theme_logo = db.Column(db.String(1000), nullable=True)
    black_theme_logo = db.Column(db.String(1000), nullable=True)
    colors = db.Column(db.JSON, nullable=True)
    fonts = db.Column(db.JSON, nullable=True)
    light_theme = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.BIGINT)
    updated_at = db.Column(db.BIGINT, nullable=True)
    branding_page = db.relationship(
        "BrandPages", backref="brand_page", lazy=True)
    branding_story = db.relationship(
        "BrandStory", backref="brand_story", lazy=True)
    brand_article_content = db.relationship(
        "BrandContent", backref="bac", lazy=True)
    brand_ssl_cert = db.relationship(
        "ssl_cert_generation", backref="brand_certs", lazy=True)
    seo_description = db.Column(db.String(1000), nullable=True)
    seo_title = db.Column(db.String(1000), nullable=True)
    favicon_img = db.Column(db.String(1000), nullable=True)
    email_api_key = db.Column(db.String(1000), nullable=True)
    terms_condition = db.Column(db.String(1000), nullable=True)
    privacy_policy = db.Column(db.String(1000), nullable=True)
    font_size = db.Column(db.BIGINT, nullable=True)
    navbar_html = db.Column(db.Text, nullable=True)
    footer_html = db.Column(db.Text, nullable=True)
    navbar_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "page_component.id"), nullable=True)
    footer_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "page_component.id"), nullable=True)
