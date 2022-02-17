from flask_restplus import Namespace, fields


class StorySharingDTO:
    api = Namespace("Brand-Story-Sharing")

    allowed_social_response = api.model("Story Sharing", {
        "socials": fields.List(fields.String, description='social support')
    })

    social_account = api.model('social account', {
        "id": fields.String(description='uuid'),
        "brand_id": fields.String(description='brand uuid'),
        "name": fields.String(description='social name'),
        "site_link": fields.String(description='social site_link'),
        "username": fields.String(description='social username'),
        "active": fields.Boolean(description='active'),
        "created_at": fields.Integer(description="Unix timestamp"),
        "updated_at": fields.Integer(description="Unix timestamp")
    })

    list_social_account = api.model('response all social accounts', {
        'items': fields.List(fields.Nested(social_account))
    })

    req_for_sharing = api.model('response all social accounts', {
        "social_accounts": fields.List(fields.String, description="Social Accounts"),
        "type": fields.String(description='sharing type'),
        "caption": fields.String(description="Captions"),
        "schedule_time": fields.Integer(description="shedule"),
        "image": fields.String(description="Imagge_link"),
        "schedule": fields.Boolean(description="schedule")
    })

    res_for_sharing = api.model('response all social accounts', {
        "id": fields.String(description='sharing log id'),
        "story_id": fields.String(description='story id'),
        "social_id": fields.String(description='story id'),
        "user_id": fields.String(description='user id'),
        "type": fields.String(description='sharing type'),
        "caption": fields.String(description="Captions"),
        "schedule": fields.Boolean(description="schedule"),
        "schedule_time": fields.Integer(description="shedule time"),
        "image_link": fields.String(description="Imagge_link"),
        "retry_count": fields.Integer(description="Imagge_link"),
        "sharing_status": fields.String(description="sharing_status"),
        "success": fields.Boolean(description="success"),
        "created_at": fields.Integer(description="Unix timestamp"),
        "updated_at": fields.Integer(description="Unix timestamp")
    })

    response_share = api.model('response after share', {
        'message': fields.String(description="share")
    })

    res_sharing_logs = api.model('response all logs', {
        'items': fields.List(fields.Nested(res_for_sharing)),
        "total_pages": fields.List(fields.Integer),
        "pages": fields.Integer(),
        "has_next": fields.Boolean(),
        "has_prev": fields.Boolean(),
        "page": fields.Integer(),
        "per_page": fields.Integer(),
        "total": fields.Integer()
    })

    account_res = api.model('response all social accounts', {
        "id": fields.String(description='account id'),
        "name": fields.String(description="name"),
        "username": fields.String(description="username")
    })

    story_res = api.model('response all social accounts', {
        "id": fields.String(description='account id'),
        "name": fields.String(description="name"),
        "link": fields.String(description="link")
    })

    res_for_sharing_log = api.model('response all social accounts', {
        "id": fields.String(description='sharing log id'),
        "caption": fields.String(description="Captions"),
        "schedule": fields.Boolean(description="schedule"),
        "schedule_time": fields.Integer(description="shedule time"),
        "image_link": fields.String(description="Imagge_link"),
        "sharing_status": fields.String(description="sharing_status"),
        "success": fields.Boolean(description="success"),
        'account': fields.Nested(account_res),
        'story': fields.Nested(story_res),
    })

    res_sharing_logs_marketing = api.model('response all logs', {
        'items': fields.List(fields.Nested(res_for_sharing_log)),
        "total_pages": fields.List(fields.Integer),
        "pages": fields.Integer(),
        "has_next": fields.Boolean(),
        "has_prev": fields.Boolean(),
        "page": fields.Integer(),
        "per_page": fields.Integer(),
        "total": fields.Integer()
    })
