from flask_restplus import Namespace, fields


class MultiUser:
    api = Namespace("MultiUser", description="multiuser API")
    email_request = api.model("send email for confirmation", {
        "brand_id": fields.String(description='Brand_id to add'),
        "email": fields.String(description="email")
    })

    email_response = api.model("response for email",{
        "message":fields.String()
    })

    expect_new_user = api.model("request Signup", {
        'password': fields.String(required=True, description='password')
    })