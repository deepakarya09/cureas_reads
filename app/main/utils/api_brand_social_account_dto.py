from flask_restplus import Namespace, fields


class SocialAccountsDto:
    api = Namespace("social_account", description="social account API")

    req_post_social_account_instagram = api.model('post social account', {
        "access_token": fields.String(description='social access token')
    })

    req_user_id = api.model('post social account access', {
        "user_id": fields.String(description='social access user')
    })

    res_message = api.model('response message', {
        "message": fields.String(description='social message response')
    })

    ig_account = api.model('post response ig account', {
        "ig_id": fields.String(description='social access id'),
        "username": fields.String(description='social access usename')
    })
    req_for_update = api.model('social account request', {
        "name": fields.String(description='social name', required=False),
        "site_link": fields.String(description='social site_link', required=False),
        "access_key": fields.String(description='social access key', required=False),
        "active": fields.Boolean(description='active', required=False)
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
    user_data = api.model("user Data", {
        "id": fields.String(),
        "first_name": fields.String(),
        "last_name": fields.String(),
        "email": fields.String(),
        "image_url": fields.String(),
        "role": fields.String(),
        "verified": fields.Boolean(description='Verification of user'),
        "login_type": fields.String(attribute="login_type"),
        "first_brand_exists": fields.Boolean(),

    })

    get_all_users = api.model("all users of brand", {
        "items": fields.List(cls_or_instance=fields.Nested(user_data))
    })

    res_all_social_accounts = api.model('response all social accounts', {
        'items': fields.List(fields.Nested(social_account))
    })

    insta_post_res = api.model('response instagram post accounts', {
        'items': fields.List(fields.Nested(ig_account))
    })

    linkedin_post_res = api.model('response linkedin post accounts', {
        'id': fields.String(description='id'),
        'username':fields.String(description='username')
    })
