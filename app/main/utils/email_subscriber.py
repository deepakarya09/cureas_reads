from flask_restplus import Namespace, fields

class EmailSubscriber:
    api = Namespace('email_subscriber', description='Subscriber for Brand')

    req_subscriber = api.model("request subscribers", {
        "email": fields.String(description='email'),
        "fqdn": fields.String(description='link')
    })

    res_subscriber = api.model("request subscribers", {
        "message":fields.String(description='response message')
    })

    res_item = api.model("response items", {
        "id":fields.String(description='id'),
        "brand_id":fields.String(description='brand_id'),
        "email":fields.String(description='email'),
        "subscribe_at":fields.String(description='created at'),
    })

    res_all_subs = api.model("response all subs",{
        'items': fields.List(fields.Nested(res_item)),
    })