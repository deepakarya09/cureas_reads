from app.main.services.email_subscribers_services import all_subs_by_brand, collect_subscriber, remove_subscriber
from app.main.utils.email_subscriber import EmailSubscriber
from http import HTTPStatus
from flask import request
from flask_restplus import Resource
from werkzeug.exceptions import abort

from app.main.controllers import error_m

api = EmailSubscriber.api
_req_subscriber = EmailSubscriber.req_subscriber
_res_subscriber = EmailSubscriber.res_subscriber
_res_all_subs = EmailSubscriber.res_all_subs

@api.route("api/v1.0/email/subscribe")
class EmailSubmission(Resource):
    @api.expect(_req_subscriber)
    @api.marshal_with(_res_subscriber)
    def post(self):
        data = request.json
        return collect_subscriber(data)

@api.route("api/v1.0/email/subscribers/<brand_id>")
class GetAllEmailSubmission(Resource):
    @api.marshal_with(_res_all_subs)
    def get(self,brand_id):
        return all_subs_by_brand(brand_id)

@api.route("api/v1.0/email/unsubscribe")
class EmailSubmission(Resource):
    @api.expect(_req_subscriber)
    @api.marshal_with(_res_subscriber)
    def delete(self):
        data = request.json
        return remove_subscriber(data)