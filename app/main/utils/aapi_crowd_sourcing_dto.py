from flask_restplus import Namespace, fields


class CrowdSourcingDto:
    api = Namespace("aapi submission crowdsourcing", description="aapi Crowdsourcing")
    res_tag = api.model("tag post response", {
        "name": fields.String(description='tag')
    })
    article = api.model("values", {
        "id": fields.String(description='uuid'),
        "title": fields.String(description='Content title'),
        "description": fields.String(description='Content description'),
        "siteLink": fields.String(attribute="site_link", description='Content site link'),
        "canonicalLink": fields.String(attribute="canonical_link", description='Content canonical link'),
        "imageLink": fields.String(attribute="image_link", description='Content image link'),
        "type": fields.String(description='Content type'),
        "country": fields.String(description='Content country'),
        "city": fields.String(description='Content city'),
        "status": fields.String(description='Content city'),
        "createdAt": fields.Integer(attribute="created_at", description="Unix timestamp"),
        "userIP": fields.String(attribute="user_ip", description='Content userIP'),
        "siteName": fields.String(attribute="site_name", description='Content site name'),
        "tags": fields.List(fields.Nested(res_tag), attribute="tag_multi_con", description="list of tags"),
        "userAgent": fields.String(attribute="user_agent"),
        "sequenceNumber": fields.Integer(required=True, attribute="sequence_number",
                                         description='article sequence number'),

    })
    return_article = api.model("Article", {
        "id": fields.String(description='uuid'),
        "workerId": fields.String(attribute="worker_id", description='uuid'),
        "workerType": fields.String(attribute="worker_type"),
        "submittedArticleCount": fields.String(attribute="submitted_article_count"),
        "confirmationCode": fields.String(attribute="confirmation_code"),
        "createdAt": fields.Integer(attribute="created_at", description="Unix timestamp"),
        "submittedAt": fields.Integer(attribute="submitted_at", description="Unix timestamp"),
        "paymentStatus": fields.Boolean(attribute="payment_status"),
        "paymentStatusUpdateAt": fields.Integer(attribute="payment_status_update_at", description="Unix timestamp"),
        "modifiedAt": fields.Integer(attribute="modified_at", description="Unix timestamp"),
        "articles": fields.List(fields.Nested(article), attribute="sub_articles", )
    })

    return_articles_by_id = api.model("Article", {
        "items": fields.List(fields.Nested(return_article), attribute="items", ),
        "page": fields.Integer(attribute="page"),
        "per_page": fields.Integer(attribute="per_page"),
        "total": fields.Integer(attribute="total"),
        "totalPages": fields.List(fields.Integer, attribute="total_pages", )
    })

    extension_return_articles_by_id = api.model("Article", {
        "items": fields.List(fields.Nested(article), attribute="items", ),
        "page": fields.Integer(attribute="page"),
        "per_page": fields.Integer(attribute="per_page"),
        "total": fields.Integer(attribute="total"),
        "totalPages": fields.List(fields.Integer, attribute="total_pages", )
    })
