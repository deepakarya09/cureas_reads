from flask_restplus import Namespace, fields


class SocialAnalyticsDto:
    api = Namespace("Social_analytics_dto", description="Brand log API")

    brand_log = api.model("brand log", {
        "name": fields.String(),
        "username": fields.String(),
        "total_post": fields.Integer(),
        "total_likes": fields.Integer(),
        "likes_percent": fields.Integer(),
        "total_comments": fields.Integer(),
        "comment_percent": fields.Integer()

    })
    res_social_analytics = api.model('social analytics response', {
        "items": fields.List(cls_or_instance=fields.Nested(brand_log)),
        "total_post": fields.Integer(),
        "post_percentage": fields.Integer(),
        "total_likes": fields.Integer(),
        "likes_percentage": fields.Integer(),
        "total_comments": fields.Integer(),
        "comments_percentage": fields.Integer()
    })
    res_social_analytics_by_id = api.model('social analytics by sharing id', {
        "image": fields.String(),
        "views": fields.Integer(),
        "interaction": fields.Integer(),
        "likes": fields.Integer(),
        "comments": fields.Integer()
    })
