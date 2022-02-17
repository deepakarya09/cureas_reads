from flask_restplus import Namespace, fields


class SslGeneration:
    api = Namespace("SslGeneration", description="ssl  API")
    ssl_request = api.model("domain name for ssl generation", {
            "site_url": fields.Url(required=True, description='domain name')

    })

    email_response = api.model("response for email",{
        "message":fields.String()
    })

    expect_new_user = api.model("request Signup", {
        'password': fields.String(required=True, description='password')
    })