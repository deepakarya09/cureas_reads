from flask_restplus import Namespace, fields


class CrowdSource:
    api = Namespace("crowd sourcing", description="crowd source API")
    worker_request = api.model("worker submission", {
        "workerId": fields.String(description='Mechanical Truck Id'),
        "workerType": fields.String(description="Worker Type")
    })

    article = api.model("Article", {
        "title": fields.String(description='Content title'),
        "description": fields.String(description='Content description'),
        "siteLink": fields.String(description='Content site link'),
        "canonicalLink": fields.String(description='Content canonical link'),
        "imageLink": fields.String(description='Content image link'),
        "type": fields.String(description='Content type'),
        "country": fields.String(description='Content country'),
        "city": fields.String(description='Content city'),
        "userIP": fields.String(description='Content userIP'),
        "siteName": fields.String(description='Content site name'),
        "tags": fields.List(fields.String, description="list of tags"),
        "sequenceNumber": fields.Integer(required=True, description='article sequence number'),
        "userAgent": fields.String(attribute="user_agent")
    })

    article_submission = api.model("worker article submission", {
        "workerId": fields.String(description="Mechanical Truck Id"),
        "article": fields.List(fields.Nested(article),),
    })

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
        "createdAt": fields.String(attribute="created_at", description='content creation time'),
        "status": fields.String(description='Content city'),
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
        "modifiedAt": fields.Integer(attribute="modified_at", description="Unix timestamp"),
        "paymentStatus": fields.Boolean(attribute="payment_status"),
        "paymentStatusUpdateAt": fields.Integer(attribute="payment_status_update_at", description="Unix timestamp"),
        "articles": fields.List(fields.Nested(article), attribute="sub_articles", )
    })
